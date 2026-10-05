"""Read a Foundry compendium stored as LevelDB.

The key layout is the one in foundryvtt-cli 0.0.6 `lib/package.mjs`
(https://github.com/foundryvtt/foundryvtt-cli/blob/main/lib/package.mjs),
retrieved 2026-10-03. That tool opens the directory with classic-level,
`keyEncoding: "utf8"` and `valueEncoding: "json"`.

Primary keys look like `!<collection>!<id>`. Embedded documents are separate
keys, `!<collection>.<field>!<parentId>.<embeddedId>`, and the parent stores
those ids. This reader puts the embedded objects back on the parent so the
inventory sees the same shape as a NeDB document. Keys that are not in that
shape are still kept when the value is a JSON object, and the key is recorded
as a diagnostic.

Values are parsed with the JSON decoder only. Nothing in a database is executed.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

# Collection names from foundryvtt-cli 0.0.6 TYPE_COLLECTION_MAP, retrieved 2026-10-03.
COLLECTION_TYPES = {
    "actors": "Actor",
    "adventures": "Adventure",
    "cards": "Cards",
    "combats": "Combat",
    "effects": "ActiveEffect",
    "fog": "FogExploration",
    "folders": "Folder",
    "items": "Item",
    "journal": "JournalEntry",
    "macros": "Macro",
    "messages": "ChatMessage",
    "playlists": "Playlist",
    "scenes": "Scene",
    "settings": "Setting",
    "tables": "RollTable",
    "users": "User",
}

# Embedded fields that the same file stores as separate keys. Array fields hold
# ids on the parent. `tokens.delta` is one object rather than an array.
HIERARCHY_ARRAYS = {
    "actors": ("items", "effects"),
    "cards": ("cards",),
    "combats": ("combatants", "groups"),
    "delta": ("items", "effects"),
    "items": ("effects",),
    "journal": ("pages", "categories"),
    "playlists": ("sounds",),
    "regions": ("behaviors",),
    "scenes": (
        "drawings",
        "tokens",
        "levels",
        "lights",
        "notes",
        "regions",
        "sounds",
        "templates",
        "tiles",
        "walls",
    ),
    "tables": ("results",),
}
HIERARCHY_OBJECTS = {
    "tokens": ("delta",),
}

PREVIEW_CHARS = 180


class LevelDBResult:
    def __init__(self) -> None:
        self.opened = False
        self.documents: list[tuple[str | None, dict]] = []
        self.diagnostics: list[tuple[str, str, str]] = []

    def warn(self, severity: str, code: str, message: str) -> None:
        self.diagnostics.append((severity, code, message))


def read_leveldb_directory(src: Path, *, max_entries: int, max_value_bytes: int) -> LevelDBResult:
    """Copy `src` to a temp directory and read it. The copy is discarded.

    LevelDB creates a LOCK file in the directory it opens. Copying first leaves
    the package fixture unchanged.
    """
    result = LevelDBResult()
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "db"
        _copy_flat(src, dest, result, max_value_bytes)
        _open_and_decode(dest, result, max_entries=max_entries, max_value_bytes=max_value_bytes)
    return result


def read_leveldb_bytes(files: dict[str, bytes], *, max_entries: int, max_value_bytes: int) -> LevelDBResult:
    """Read LevelDB files already held in memory, keyed by file name."""
    result = LevelDBResult()
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "db"
        dest.mkdir()
        for name, data in files.items():
            if "/" in name or name in {"", ".", ".."}:
                result.warn("warning", "leveldb-skipped-name", "Skipped a LevelDB entry whose name leaves the pack directory.")
                continue
            if len(data) > max_value_bytes:
                result.warn("warning", "entry-too-large", "Skipped a LevelDB file that exceeds the read budget.")
                continue
            (dest / name).write_bytes(data)
        _open_and_decode(dest, result, max_entries=max_entries, max_value_bytes=max_value_bytes)
    return result


def _copy_flat(src: Path, dest: Path, result: LevelDBResult, max_value_bytes: int) -> None:
    dest.mkdir()
    try:
        children = list(src.iterdir())
    except OSError as exc:
        result.warn("warning", "leveldb-not-decoded", f"LevelDB directory could not be listed: {type(exc).__name__}.")
        return
    for child in children:
        if child.is_symlink() or not child.is_file():
            if child.is_symlink():
                result.warn("warning", "symlink-skipped", "Skipped a symlink inside a LevelDB directory. It was not followed.")
            continue
        try:
            size = child.stat().st_size
        except OSError as exc:
            result.warn("warning", "unreadable-file", f"Could not stat a LevelDB file: {type(exc).__name__}.")
            continue
        if size > max_value_bytes:
            result.warn("warning", "entry-too-large", "Skipped a LevelDB file that exceeds the read budget.")
            continue
        try:
            (dest / child.name).write_bytes(child.read_bytes())
        except OSError as exc:
            result.warn("warning", "unreadable-file", f"Could not copy a LevelDB file: {type(exc).__name__}.")


def _open_and_decode(dest: Path, result: LevelDBResult, *, max_entries: int, max_value_bytes: int) -> None:
    try:
        import plyvel_next as plyvel
    except ImportError as exc:
        raise LevelDBUnavailable("reading LevelDB requires plyvel-next==2.1.2") from exc
    try:
        database = plyvel.DB(os.fspath(dest), create_if_missing=False)
    except plyvel.Error as exc:
        result.warn(
            "warning",
            "leveldb-not-decoded",
            "LevelDB directory could not be opened. It was not read as text and was not executed. "
            + _safe_exc(exc),
        )
        return
    result.opened = True
    raw: list[tuple[str, object]] = []
    embedded: dict[str, dict] = {}
    try:
        seen = 0
        for key_bytes, value_bytes in database:
            seen += 1
            if seen > max_entries:
                result.warn("warning", "too-many-entries", "Stopped reading because the LevelDB pack has too many entries.")
                break
            if len(value_bytes) > max_value_bytes:
                result.warn("warning", "entry-too-large", "Skipped a LevelDB value that exceeds the read budget.")
                continue
            key = _decode_key(key_bytes, result)
            if key is None:
                continue
            value = _decode_value(key, value_bytes, result)
            if not isinstance(value, dict):
                continue
            collection = _collection(key)
            if collection is not None and "." in collection:
                embedded[key] = value
            else:
                raw.append((key, value))
    finally:
        database.close()

    for key, document in raw:
        collection = _collection(key)
        if collection is None:
            result.warn(
                "info",
                "leveldb-key-unscoped",
                f"LevelDB key {key!r} is not !<collection>!<id>. The JSON object was still inventoried.",
            )
            document_type = None
        else:
            document_type = COLLECTION_TYPES.get(collection)
            if document_type is None:
                result.warn(
                    "info",
                    "leveldb-collection-unknown",
                    f"LevelDB collection {collection!r} is not in the foundryvtt-cli collection map. "
                    "The document was inventoried with the pack's declared type.",
                )
                document_type = None
            _rehydrate(document, collection, embedded, result)
        result.documents.append((document_type, document))

    for key in sorted(embedded):
        result.warn(
            "info",
            "leveldb-embedded-unattached",
            f"LevelDB embedded key {key!r} did not match a parent id list. The object was inventoried on its own.",
        )
        collection = _collection(key)
        field = collection.split(".", 1)[1] if collection and "." in collection else None
        document_type = _field_type(field) if field else None
        result.documents.append((document_type, embedded[key]))


def _rehydrate(document: dict, collection: str, embedded: dict[str, dict], result: LevelDBResult) -> None:
    parent_id = document.get("_id")
    for field in HIERARCHY_ARRAYS.get(collection, ()):
        values = document.get(field)
        if isinstance(values, list) and values and all(isinstance(item, str) for item in values) and isinstance(parent_id, str):
            rebuilt = []
            for embedded_id in values:
                key = f"!{collection}.{field}!{parent_id}.{embedded_id}"
                found = embedded.pop(key, None)
                if isinstance(found, dict):
                    _rehydrate(found, field, embedded, result)
                    rebuilt.append(found)
                else:
                    result.warn(
                        "warning",
                        "leveldb-embedded-missing",
                        f"LevelDB parent {parent_id!r} lists {field} id {embedded_id!r} and that key was not in the database.",
                    )
                    rebuilt.append({"_id": embedded_id})
            document[field] = rebuilt
        elif isinstance(values, list):
            for item in values:
                if isinstance(item, dict):
                    _rehydrate(item, field, embedded, result)
    for field in HIERARCHY_OBJECTS.get(collection, ()):
        value = document.get(field)
        if isinstance(value, str) and isinstance(parent_id, str):
            key = f"!{collection}.{field}!{parent_id}.{value}"
            found = embedded.pop(key, None)
            if isinstance(found, dict):
                _rehydrate(found, field, embedded, result)
                document[field] = found
        elif isinstance(value, dict):
            _rehydrate(value, field, embedded, result)


def _field_type(field: str) -> str | None:
    return {
        "effects": "ActiveEffect",
        "items": "Item",
        "pages": "JournalEntryPage",
        "categories": "JournalEntryCategory",
        "sounds": "AmbientSound",
        "results": "TableResult",
        "cards": "Card",
        "combatants": "Combatant",
        "behaviors": "RegionBehavior",
        "walls": "Wall",
        "lights": "AmbientLight",
        "tokens": "Token",
        "tiles": "Tile",
        "drawings": "Drawing",
        "notes": "Note",
        "regions": "Region",
        "levels": "Level",
    }.get(field)


def _collection(key: str) -> str | None:
    parts = key.split("!")
    if len(parts) < 3 or parts[0] != "":
        return None
    collection = parts[1]
    if not collection:
        return None
    return collection


def _decode_key(key_bytes: bytes, result: LevelDBResult) -> str | None:
    try:
        return key_bytes.decode("utf-8")
    except UnicodeDecodeError:
        result.warn(
            "warning",
            "leveldb-key-not-text",
            "A LevelDB key is not UTF-8. The entry was not decoded and was not executed.",
        )
        return None


def _decode_value(key: str, value_bytes: bytes, result: LevelDBResult) -> object | None:
    try:
        text = value_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        result.warn(
            "warning",
            "leveldb-value-not-document",
            f"LevelDB key {key!r} is not UTF-8 JSON. The value was not decoded and was not executed.",
        )
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        preview = text[:PREVIEW_CHARS].replace("\n", " ")
        result.warn(
            "warning",
            "leveldb-value-not-document",
            f"LevelDB key {key!r} is not a JSON value and was not executed. Preview: {preview}",
        )
        return None


def _safe_exc(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}".splitlines()[0]
    for banned in ("writeFileSync", "/tmp/forgebridge"):
        text = text.replace(banned, "[redacted]")
    return text[:180]


class LevelDBUnavailable(Exception):
    """plyvel is not installed."""
