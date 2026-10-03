"""Read a Foundry package and build an inventory document.

Archives, paths, HTML, filenames, and macro text are treated as hostile data.
Nothing in an imported package is passed to an interpreter.
"""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from pathlib import Path

from forgebridge import IR_VERSION, __version__
from forgebridge.validate import InventoryFatal

MAX_ENTRY_BYTES = 8_000_000
MAX_TOTAL_BYTES = 32_000_000
MAX_ENTRIES = 4_000
MAX_RETAINED_CHARS = 4_000
MAX_PREVIEW_CHARS = 180

MANIFEST_NAMES = ("module.json", "world.json", "system.json")
TEXT_SUFFIXES = {".json", ".db", ".js", ".mjs", ".cjs", ".css", ".html", ".htm", ".md", ".txt"}
ASSET_KEYS = {"src", "img", "path", "thumb", "video"}
CODE_KEYS = {"command", "script"}
ACTIVE_MARKERS = ("<script", "javascript:", "onerror=", "onload=")

MEDIA_KINDS = {
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".svg": "image",
    ".gif": "animation",
    ".mp4": "video",
    ".m4v": "video",
    ".webm": "video",
    ".mp3": "audio",
    ".ogg": "audio",
    ".wav": "audio",
    ".flac": "audio",
    ".ttf": "font",
    ".otf": "font",
    ".woff": "font",
    ".woff2": "font",
    ".pdf": "other",
}

DOMAIN_ORDER = (
    "assets",
    "maps",
    "geometry",
    "presentation",
    "entities",
    "knowledge",
    "audio",
    "tables",
    "behaviors",
)

PRIMARY_DOMAINS = {
    "Scene": ["maps"],
    "Actor": ["entities"],
    "Item": ["entities"],
    "JournalEntry": ["knowledge"],
    "RollTable": ["tables"],
    "Playlist": ["audio"],
    "Macro": ["behaviors"],
    "ActiveEffect": ["behaviors"],
}

EMBEDDED_DOMAIN = {
    "Wall": "geometry",
    "Drawing": "geometry",
    "Region": "geometry",
    "AmbientLight": "presentation",
    "Level": "presentation",
    "Token": "entities",
    "ActorDelta": "entities",
    "Item": "entities",
    "Note": "knowledge",
    "JournalEntryPage": "knowledge",
    "JournalEntryCategory": "knowledge",
    "AmbientSound": "audio",
    "PlaylistSound": "audio",
    "TableResult": "tables",
    "RegionBehavior": "behaviors",
    "ActiveEffect": "behaviors",
    "Tile": "assets",
}

# Top-level keys confirmed from the Version 14 API pages cited in the research note.
# Types without a pinned list keep their whole source document instead of being guessed.
PINNED_KEYS = {
    "Scene": {
        "_id", "_stats", "active", "backgroundColor", "drawings", "environment", "flags",
        "fog", "folder", "grid", "height", "initial", "initialLevel", "journal",
        "journalEntryPage", "levels", "lights", "name", "navigation", "navName",
        "navOrder", "notes", "ownership", "padding", "playlist", "playlistSound",
        "regions", "shiftX", "shiftY", "sort", "sounds", "thumb", "tiles", "tokens",
        "tokenVision", "transition", "walls", "weather", "width",
    },
    "Macro": {
        "_id", "_stats", "author", "command", "flags", "folder", "img", "name",
        "ownership", "scope", "sort", "type",
    },
}

MANIFEST_KEYS = {
    "authors", "background", "bugs", "changelog", "compatibility", "coreTranslation",
    "coreVersion", "demo", "description", "documentTypes", "download", "esmodules",
    "exclusive", "flags", "grid", "id", "initiative", "joinTheme", "languages",
    "library", "license", "manifest", "media", "nextSession", "packFolders", "packs",
    "persistentStorage", "primaryTokenAttribute", "protected", "quickstart", "readme",
    "relationships", "resetKeys", "safeMode", "scripts", "secondaryTokenAttribute",
    "socket", "styles", "system", "systemVersion", "title", "type", "url", "version",
}

WORLD_COLLECTIONS = {
    "actors": "Actor",
    "items": "Item",
    "scenes": "Scene",
    "journal": "JournalEntry",
    "tables": "RollTable",
    "playlists": "Playlist",
    "macros": "Macro",
    "cards": "Cards",
    "folders": "Folder",
    "combats": "Combat",
    "messages": "ChatMessage",
    "settings": "Setting",
    "users": "User",
    "fog": "FogExploration",
}

COMPENDIUM_TYPES = {
    "ActiveEffect", "Actor", "Adventure", "Cards", "Item", "JournalEntry",
    "Macro", "Playlist", "RollTable", "Scene",
}


class FileRec:
    def __init__(self, relpath: str, size: int, data: bytes | None):
        self.relpath = relpath
        self.size = size
        self.data = data


class Store:
    def __init__(self):
        self.files: dict[str, FileRec] = {}
        self.diagnostics: list[dict] = []
        self.bytes_read = 0

    def add(self, rec: FileRec) -> None:
        self.files[rel_key(rec.relpath)] = rec

    def get(self, relpath: str) -> FileRec | None:
        return self.files.get(rel_key(relpath))

    def warn(self, severity: str, code: str, message: str, path: str = "") -> None:
        self.diagnostics.append(
            {"severity": severity, "code": code, "message": message, "path": path}
        )


def rel_key(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def inventory_path(path: Path) -> dict:
    if not path.exists():
        raise InventoryFatal(f"package path does not exist: {path}")
    if path.is_dir():
        store, source_name = _read_directory(path)
        input_form = "directory"
        archive_name = None
    elif path.is_file():
        store, source_name = _read_zip(path)
        input_form = "zip"
        archive_name = path.name
    else:
        raise InventoryFatal(f"package path is not a file or directory: {path}")

    manifest_rel, manifest = _load_manifest(store)
    return _build(
        store,
        manifest_rel,
        manifest,
        input_form=input_form,
        source_name=source_name,
        archive_name=archive_name,
    )


def _read_directory(root: Path) -> tuple[Store, str]:
    store = Store()
    root_resolved = root.resolve()
    count = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        kept_dirs = []
        for dirname in dirnames:
            candidate = Path(dirpath) / dirname
            if candidate.is_symlink() or not _inside(root_resolved, candidate):
                store.warn(
                    "warning",
                    "symlink-skipped",
                    "Skipped a directory symlink or path that leaves the package root.",
                    _display_rel(root, candidate),
                )
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for filename in filenames:
            count += 1
            if count > MAX_ENTRIES:
                store.warn("error", "too-many-entries", "Stopped reading because the package has too many files.", "")
                return store, root.name
            candidate = Path(dirpath) / filename
            display = _display_rel(root, candidate)
            if candidate.is_symlink() or not _inside(root_resolved, candidate):
                store.warn(
                    "warning",
                    "symlink-skipped",
                    "Skipped a symlink or path that leaves the package root.",
                    display,
                )
                continue
            try:
                size = candidate.stat().st_size
            except OSError as exc:
                store.warn("warning", "unreadable-file", f"Could not stat file: {exc}", display)
                continue
            data = _read_limited(store, candidate, size, display)
            store.add(FileRec(display, size, data))
    return store, root.name


def _read_limited(store: Store, path: Path, size: int, display: str) -> bytes | None:
    suffix = path.suffix.lower()
    if suffix not in TEXT_SUFFIXES:
        return None
    if size > MAX_ENTRY_BYTES or store.bytes_read + size > MAX_TOTAL_BYTES:
        store.warn("warning", "entry-too-large", "Skipped a text file that exceeds the read budget.", display)
        return None
    try:
        data = path.read_bytes()
    except OSError as exc:
        store.warn("warning", "unreadable-file", f"Could not read file: {exc}", display)
        return None
    store.bytes_read += len(data)
    return data


def _display_rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except (OSError, ValueError):
        return False
    return True


def _read_zip(path: Path) -> tuple[Store, str]:
    store = Store()
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile as exc:
        raise InventoryFatal(f"not a zip archive: {path}") from exc
    source_name = path.stem
    with zf:
        infos = zf.infolist()
        if len(infos) > MAX_ENTRIES:
            store.warn("error", "too-many-entries", "Stopped reading because the archive has too many entries.", path.name)
            infos = infos[:MAX_ENTRIES]
        kept: dict[str, bytes | None] = {}
        sizes: dict[str, int] = {}
        for info in infos:
            if info.is_dir() or info.filename.endswith("/"):
                continue
            rel, reason = _safe_zip_name(info.filename)
            if rel is None:
                store.warn(
                    "warning",
                    "rejected-zip-entry",
                    f"Rejected zip entry ({reason}). The entry was not extracted or run.",
                    info.filename,
                )
                continue
            if info.file_size > MAX_ENTRY_BYTES or store.bytes_read >= MAX_TOTAL_BYTES:
                store.warn("warning", "entry-too-large", "Skipped a zip entry that exceeds the read budget.", rel)
                kept[rel] = None
                sizes[rel] = info.file_size
                continue
            suffix = Path(rel).suffix.lower()
            data: bytes | None = None
            if suffix in TEXT_SUFFIXES:
                with zf.open(info, "r") as handle:
                    data = handle.read(MAX_ENTRY_BYTES + 1)
                if len(data) > MAX_ENTRY_BYTES or store.bytes_read + len(data) > MAX_TOTAL_BYTES:
                    store.warn("warning", "entry-too-large", "Skipped a zip entry that exceeds the read budget.", rel)
                    data = None
                else:
                    store.bytes_read += len(data)
            kept[rel] = data
            sizes[rel] = info.file_size
        kept, sizes, source_name = _strip_single_root(kept, sizes, source_name)
        for rel, data in kept.items():
            store.add(FileRec(rel, sizes[rel], data))
    return store, source_name


def _safe_zip_name(name: str) -> tuple[str | None, str | None]:
    if "\x00" in name:
        return None, "null-byte"
    if name.startswith("/") or name.startswith("\\"):
        return None, "absolute"
    if len(name) >= 2 and name[1] == ":":
        return None, "drive"
    parts: list[str] = []
    for part in name.replace("\\", "/").split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            return None, "traversal"
        parts.append(part)
    if not parts:
        return None, "empty"
    return "/".join(parts), None


def _strip_single_root(
    files: dict[str, bytes | None],
    sizes: dict[str, int],
    source_name: str,
) -> tuple[dict[str, bytes | None], dict[str, int], str]:
    if any(name in files for name in MANIFEST_NAMES):
        return files, sizes, source_name
    manifests = [
        name for name in files
        if name.count("/") == 1 and Path(name).name in MANIFEST_NAMES
    ]
    if len(manifests) != 1:
        return files, sizes, source_name
    prefix = manifests[0].split("/")[0]
    prefix_slash = prefix + "/"
    if not all(name.startswith(prefix_slash) for name in files):
        return files, sizes, source_name
    stripped = {name[len(prefix_slash):]: data for name, data in files.items()}
    stripped_sizes = {name[len(prefix_slash):]: sizes[name] for name in files}
    return stripped, stripped_sizes, prefix


def _load_manifest(store: Store) -> tuple[str, dict]:
    for name in MANIFEST_NAMES:
        rec = store.get(name)
        if rec is None:
            continue
        if rec.data is None:
            raise InventoryFatal(f"{name} was not readable")
        try:
            parsed = json.loads(rec.data.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise InventoryFatal(f"{name} is not JSON and was not executed: {exc}") from exc
        if not isinstance(parsed, dict):
            raise InventoryFatal(f"{name} is not a JSON object")
        return name, parsed
    raise InventoryFatal("no module.json, world.json, or system.json found")


def _build(
    store: Store,
    manifest_rel: str,
    manifest: dict,
    *,
    input_form: str,
    source_name: str,
    archive_name: str | None,
) -> dict:
    file_kind = {"module.json": "module", "world.json": "world", "system.json": "system"}[manifest_rel]
    declared = manifest.get("type")
    if declared in {"module", "world", "system"} and declared != file_kind:
        store.warn(
            "warning",
            "manifest-type-filename-mismatch",
            f"Manifest type {declared!r} does not match {manifest_rel}; the filename was used.",
            manifest_rel,
        )
    package_id = manifest.get("id") if isinstance(manifest.get("id"), str) else None
    if package_id and package_id != source_name:
        store.warn(
            "warning",
            "manifest-id-folder-mismatch",
            f"Manifest id {package_id!r} does not match folder name {source_name!r}.",
            manifest_rel,
        )
    title = manifest.get("title") if isinstance(manifest.get("title"), str) else None
    version = manifest.get("version")
    version_text = None if version is None else str(version)
    system = None
    system_requirement: list[str] = []
    raw_system = manifest.get("system")
    if file_kind == "world" and isinstance(raw_system, str):
        system = raw_system
    elif file_kind == "system":
        system = package_id
    elif isinstance(raw_system, list):
        system_requirement = [item for item in raw_system if isinstance(item, str)]
    compatibility = manifest.get("compatibility") if isinstance(manifest.get("compatibility"), dict) else {}
    relationships = manifest.get("relationships") if isinstance(manifest.get("relationships"), dict) else {}
    document_types = manifest.get("documentTypes")
    declared_types = sorted(document_types.keys()) if isinstance(document_types, dict) else []
    authors = _authors(manifest.get("authors"))
    unmapped = {
        key: _truncate(value)
        for key, value in manifest.items()
        if key not in MANIFEST_KEYS
    }
    if unmapped:
        store.warn(
            "info",
            "unmapped-manifest-fields",
            "Manifest fields outside the documented set were retained.",
            manifest_rel,
        )

    scripts = _code_files(store, manifest.get("scripts"), "package-script-not-executed", "Package script was not executed.")
    scripts += _code_files(store, manifest.get("esmodules"), "package-script-not-executed", "Package ES module was not executed.")
    styles = _code_files(store, manifest.get("styles"), "stylesheet-not-applied", "Stylesheet was not applied.")

    documents: list[dict] = []
    packs: list[dict] = []
    behaviors: list[dict] = []
    asset_hits: list[dict] = []
    seen_paths: set[str] = set()
    pinned_noted: set[str] = set()

    for pack in manifest.get("packs") or []:
        if not isinstance(pack, dict):
            store.warn("warning", "pack-not-object", "A manifest pack entry was not an object and was retained only as a warning.", manifest_rel)
            continue
        record, new_docs = _read_pack(
            store,
            pack,
            behaviors=behaviors,
            asset_hits=asset_hits,
            pinned_noted=pinned_noted,
        )
        packs.append(record)
        documents.extend(new_docs)
        if record.get("path"):
            seen_paths.add(record["path"])

    if file_kind == "world":
        _read_world_data(
            store,
            system=system,
            packs=packs,
            documents=documents,
            behaviors=behaviors,
            asset_hits=asset_hits,
            pinned_noted=pinned_noted,
            seen_paths=seen_paths,
        )

    assets = _assemble_assets(store, asset_hits)
    _note_pack_type_rules(store, packs)

    counts = _counts(documents, assets, behaviors, store.diagnostics)
    diagnostics = _sorted_diagnostics(store.diagnostics)
    counts["diagnostics"] = len(diagnostics)

    return {
        "ir_version": IR_VERSION,
        "kind": "inventory",
        "generator": {"name": "forgebridge-inventory", "version": __version__},
        "provenance": {
            "input_form": input_form,
            "source_name": source_name,
            "archive_name": archive_name,
            "package_type": file_kind,
            "package_id": package_id,
            "title": title,
            "version": version_text,
            "system": system,
            "system_requirement": system_requirement,
            "compatibility": compatibility,
            "relationships": relationships,
            "manifest_path": manifest_rel,
            "manifest": json.loads(json.dumps(manifest)),
            "manifest_unmapped": unmapped,
            "declared_document_types": declared_types,
            "authors": authors,
            "scripts_not_executed": scripts,
            "styles_not_applied": styles,
        },
        "packs": packs,
        "documents": documents,
        "assets": assets,
        "behaviors": behaviors,
        "diagnostics": diagnostics,
        "counts": counts,
    }


def _authors(raw: object) -> list[str]:
    names: list[str] = []
    if not isinstance(raw, list):
        return names
    for item in raw:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict) and isinstance(item.get("name"), str):
            names.append(item["name"])
    return names


def _code_files(store: Store, raw: object, code: str, message: str) -> list[dict]:
    found: list[dict] = []
    if not isinstance(raw, list):
        return found
    for item in raw:
        if not isinstance(item, str):
            continue
        safe, problem = _safe_ref(item)
        if problem:
            store.warn("warning", problem, "Manifest path was rejected and the target was not read or run.", item)
            found.append({"path": item, "sha256": None, "bytes": None, "executed": False, "preview": ""})
            continue
        rec = store.get(safe or "")
        digest = None
        size = None
        preview = ""
        if rec is None or rec.data is None:
            store.warn("warning", "missing-package-file", "Manifest file was not in the package.", item)
        else:
            digest = hashlib.sha256(rec.data).hexdigest()
            size = len(rec.data)
            preview = rec.data.decode("utf-8", errors="replace")[:MAX_PREVIEW_CHARS]
        store.warn("warning" if code == "package-script-not-executed" else "info", code, message, item)
        found.append({"path": item, "sha256": digest, "bytes": size, "executed": False, "preview": preview})
    return found


def _read_pack(
    store: Store,
    pack: dict,
    *,
    behaviors: list[dict],
    asset_hits: list[dict],
    pinned_noted: set[str],
    name_override: str | None = None,
    path_override: str | None = None,
    type_override: str | None = None,
) -> tuple[dict, list[dict]]:
    name = name_override or (pack.get("name") if isinstance(pack.get("name"), str) else None)
    label = pack.get("label") if isinstance(pack.get("label"), str) else None
    document_type = type_override or (pack.get("type") if isinstance(pack.get("type"), str) else None)
    system = pack.get("system") if isinstance(pack.get("system"), str) else None
    raw_path = path_override or (pack.get("path") if isinstance(pack.get("path"), str) else None)
    safe_path, problem = _safe_ref(raw_path) if raw_path else (None, None)
    if problem:
        store.warn("warning", problem, "Pack path was rejected and was not read.", raw_path or "")
        return _pack_record(name, label, document_type, system, raw_path, "missing", False, 0), []
    if safe_path is None:
        store.warn("warning", "pack-missing", "Pack has no path.", name or "")
        return _pack_record(name, label, document_type, system, None, "missing", False, 0), []

    storage, decoded, payloads = _open_pack_storage(store, safe_path)
    documents: list[dict] = []
    if decoded:
        for index, payload in enumerate(payloads):
            documents.append(
                _document_from_payload(
                    store,
                    payload,
                    document_type=document_type or "Unknown",
                    pack_name=name,
                    storage=storage,
                    source_path=safe_path,
                    source_index=index,
                    behaviors=behaviors,
                    asset_hits=asset_hits,
                    pinned_noted=pinned_noted,
                )
            )
    return (
        _pack_record(name, label, document_type, system, safe_path, storage, decoded, len(documents)),
        documents,
    )


def _pack_record(name, label, document_type, system, path, storage, decoded, count) -> dict:
    return {
        "name": name,
        "label": label,
        "document_type": document_type,
        "system": system,
        "path": path,
        "storage": storage,
        "decoded": decoded,
        "document_count": count,
    }


def _open_pack_storage(store: Store, path: str) -> tuple[str, bool, list[dict]]:
    suffix = Path(path).suffix.lower()
    rec = store.get(path)
    if _is_dir(store, path):
        if _is_leveldb(store, path):
            store.warn(
                "warning",
                "leveldb-not-decoded",
                "LevelDB pack directory was recognized and not decoded. Binary contents were not executed.",
                path,
            )
            return "leveldb", False, []
        children = _child_files(store, path)
        if children and all(name.endswith(".json") for name in children):
            payloads: list[dict] = []
            for child in children:
                payloads.extend(_payloads_from_json(store, child))
            return "json", True, payloads
        store.warn("warning", "pack-not-text", "Pack directory is not LevelDB and not a directory of JSON documents.", path)
        return "missing", False, []
    if rec is None:
        store.warn("warning", "pack-missing", "Pack path does not exist in the package.", path)
        return "missing", False, []
    if suffix in {".yaml", ".yml"}:
        store.warn(
            "warning",
            "yaml-not-decoded",
            "YAML pack was not parsed. The official unpack tool can emit YAML; this spike does not load it.",
            path,
        )
        return "yaml", False, []
    if suffix == ".json":
        return "json", True, _payloads_from_json(store, path)
    if rec.data is None:
        store.warn("warning", "pack-not-text", "Pack file was not loaded as text.", path)
        return "missing", False, []
    return "nedb", True, _payloads_from_jsonl(store, path, rec.data)


def _is_dir(store: Store, path: str) -> bool:
    prefix = path.rstrip("/") + "/"
    return any(name.startswith(prefix) for name in store.files)


def _is_leveldb(store: Store, path: str) -> bool:
    names = {Path(child).name for child in _child_files(store, path)}
    if "CURRENT" in names:
        return True
    if any(name.startswith("MANIFEST") for name in names):
        return True
    return any(name.endswith(".ldb") or name.endswith(".sst") for name in names)


def _child_files(store: Store, path: str) -> list[str]:
    prefix = path.rstrip("/") + "/"
    children = []
    for name in store.files:
        if not name.startswith(prefix):
            continue
        rest = name[len(prefix):]
        if rest and "/" not in rest:
            children.append(name)
    return sorted(children)


def _payloads_from_json(store: Store, path: str) -> list[dict]:
    rec = store.get(path)
    if rec is None or rec.data is None:
        store.warn("warning", "document-not-json", "JSON pack file was not readable.", path)
        return []
    try:
        parsed = json.loads(rec.data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        store.warn("warning", "document-not-json", "JSON pack file was not valid JSON and was not executed.", path)
        return []
    if isinstance(parsed, list):
        docs = [item for item in parsed if isinstance(item, dict)]
        if len(docs) != len(parsed):
            store.warn("warning", "document-not-json", "Non-object JSON array entries were skipped.", path)
        return docs
    if isinstance(parsed, dict):
        return [parsed]
    store.warn("warning", "document-not-json", "JSON pack file was not an object or array.", path)
    return []


def _payloads_from_jsonl(store: Store, path: str, data: bytes) -> list[dict]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        store.warn("warning", "pack-not-text", "Pack file is not UTF-8 text. It was not decoded or executed.", path)
        return []
    payloads = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            store.warn(
                "warning",
                "document-not-json",
                f"Line {line_number} is not JSON and was not executed.",
                path,
            )
            continue
        if isinstance(parsed, dict):
            payloads.append(parsed)
        else:
            store.warn("warning", "document-not-json", f"Line {line_number} is not a JSON object.", path)
    return payloads


def _document_from_payload(
    store: Store,
    payload: dict,
    *,
    document_type: str,
    pack_name: str | None,
    storage: str,
    source_path: str,
    source_index: int,
    behaviors: list[dict],
    asset_hits: list[dict],
    pinned_noted: set[str],
) -> dict:
    doc_id = payload.get("_id") if isinstance(payload.get("_id"), str) else None
    if doc_id is None and isinstance(payload.get("id"), str):
        doc_id = payload["id"]
    name = payload.get("name") if isinstance(payload.get("name"), str) else None
    subtype = payload.get("type") if isinstance(payload.get("type"), str) else None
    embedded_counts, door_codes = _walk_embedded(
        store,
        payload,
        document_type,
        source_path=source_path,
        parent_id=doc_id,
        behaviors=behaviors,
    )
    refs = _walk_assets(store, payload, document_type, doc_id, asset_hits, source_path)
    retained, flag_scopes = _retain(store, payload, document_type, source_path, pinned_noted)
    domains = _domains(document_type, embedded_counts, refs)
    if document_type == "Macro":
        _add_behavior(
            behaviors,
            kind="macro",
            payload_value=payload.get("command") if isinstance(payload.get("command"), str) else payload,
            source_path=source_path,
            doc_id=doc_id,
            name=name,
            macro_type=subtype,
        )
    return {
        "document_type": document_type,
        "id": doc_id,
        "name": name,
        "subtype": subtype,
        "domains": domains,
        "pack": pack_name,
        "storage": storage,
        "source_path": source_path,
        "source_index": source_index,
        "embedded_counts": embedded_counts,
        "asset_refs": refs,
        "flag_scopes": flag_scopes,
        "retained_fields": retained,
        "door_codes": door_codes,
    }


def _walk_embedded(
    store: Store,
    node: dict,
    parent_type: str,
    *,
    source_path: str,
    parent_id: str | None,
    behaviors: list[dict],
    depth: int = 0,
) -> tuple[dict, list[int]]:
    counts: dict[str, int] = {}
    door_codes: set[int] = set()
    if depth > 8 or not isinstance(node, dict):
        return counts, []
    for key, value in node.items():
        embedded = _embedded_type(parent_type, key)
        if embedded is None or not isinstance(value, list):
            continue
        for item in value:
            if not isinstance(item, dict):
                continue
            counts[embedded] = counts.get(embedded, 0) + 1
            if embedded == "Wall":
                door = item.get("door")
                if isinstance(door, int) and not isinstance(door, bool):
                    door_codes.add(door)
            if embedded in {"RegionBehavior", "ActiveEffect"}:
                _add_behavior(
                    behaviors,
                    kind="region-behavior" if embedded == "RegionBehavior" else "active-effect",
                    payload_value=_behavior_payload(item),
                    source_path=source_path,
                    doc_id=item.get("_id") if isinstance(item.get("_id"), str) else parent_id,
                    name=item.get("name") if isinstance(item.get("name"), str) else None,
                    macro_type=item.get("type") if isinstance(item.get("type"), str) else None,
                )
            child_counts, child_doors = _walk_embedded(
                store,
                item,
                embedded,
                source_path=source_path,
                parent_id=item.get("_id") if isinstance(item.get("_id"), str) else parent_id,
                behaviors=behaviors,
                depth=depth + 1,
            )
            for child_type, child_count in child_counts.items():
                counts[child_type] = counts.get(child_type, 0) + child_count
            door_codes.update(child_doors)
    ordered = {key: counts[key] for key in sorted(counts)}
    return ordered, sorted(door_codes)


def _embedded_type(parent_type: str, key: str) -> str | None:
    if key == "sounds" and parent_type == "Playlist":
        return "PlaylistSound"
    if key == "sounds" and parent_type == "Scene":
        return "AmbientSound"
    mapping = {
        "walls": "Wall",
        "lights": "AmbientLight",
        "tokens": "Token",
        "tiles": "Tile",
        "drawings": "Drawing",
        "notes": "Note",
        "regions": "Region",
        "levels": "Level",
        "pages": "JournalEntryPage",
        "categories": "JournalEntryCategory",
        "items": "Item",
        "effects": "ActiveEffect",
        "results": "TableResult",
        "cards": "Card",
        "combatants": "Combatant",
        "behaviors": "RegionBehavior",
    }
    if key == "behaviors" and parent_type not in {"Region", "Scene"}:
        return None
    if key == "behaviors" and parent_type == "Scene":
        return None
    return mapping.get(key)


def _behavior_payload(item: dict) -> object:
    if isinstance(item.get("command"), str):
        return item["command"]
    if isinstance(item.get("script"), str):
        return item["script"]
    system = item.get("system")
    if isinstance(system, dict) and isinstance(system.get("script"), str):
        return system["script"]
    return item


def _add_behavior(
    behaviors: list[dict],
    *,
    kind: str,
    payload_value: object,
    source_path: str,
    doc_id: str | None,
    name: str | None,
    macro_type: str | None,
) -> None:
    encoded = payload_value if isinstance(payload_value, str) else json.dumps(payload_value, sort_keys=True, default=str)
    behaviors.append(
        {
            "kind": kind,
            "id": doc_id,
            "name": name,
            "macro_type": macro_type,
            "interpreted": False,
            "executed": False,
            "source_path": source_path,
            "document_id": doc_id,
            "payload_sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
            "payload": _truncate(payload_value),
        }
    )


def _walk_assets(
    store: Store,
    node: object,
    document_type: str,
    doc_id: str | None,
    asset_hits: list[dict],
    source_path: str,
    field_path: str = "",
) -> list[str]:
    refs: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{field_path}.{key}" if field_path else key
            if key in CODE_KEYS and isinstance(value, str):
                _note_active(store, value, source_path)
                store.warn(
                    "warning",
                    "script-body-not-parsed",
                    "Code-like text was retained as data and was not parsed or executed.",
                    source_path,
                )
                continue
            if isinstance(value, str):
                _note_active(store, value, source_path)
                if key in ASSET_KEYS and value.strip():
                    refs.append(value)
                    asset_hits.append(
                        {
                            "ref": value,
                            "document_type": document_type,
                            "id": doc_id,
                            "field": child,
                        }
                    )
            else:
                refs.extend(
                    _walk_assets(store, value, document_type, doc_id, asset_hits, source_path, child)
                )
    elif isinstance(node, list):
        for index, item in enumerate(node):
            child = f"{field_path}.{index}" if field_path else str(index)
            refs.extend(_walk_assets(store, item, document_type, doc_id, asset_hits, source_path, child))
    return sorted(set(refs))


def _note_active(store: Store, value: str, source_path: str) -> None:
    lowered = value.lower()
    if any(marker in lowered for marker in ACTIVE_MARKERS):
        store.warn(
            "warning",
            "active-content-not-interpreted",
            "Text contains HTML or a script URL and was not rendered or executed.",
            source_path,
        )


def _retain(
    store: Store,
    payload: dict,
    document_type: str,
    source_path: str,
    pinned_noted: set[str],
) -> tuple[dict, list[str]]:
    flags = payload.get("flags")
    flag_scopes = sorted(flags.keys()) if isinstance(flags, dict) else []
    allow = PINNED_KEYS.get(document_type)
    if allow is None:
        if document_type not in pinned_noted:
            pinned_noted.add(document_type)
            store.warn(
                "info",
                "schema-not-pinned",
                "This document type has no field allow-list in the spike, so the source object was retained.",
                document_type,
            )
        return {"_unpinned_source": _truncate(payload)}, flag_scopes
    retained = {}
    unknown = []
    for key, value in payload.items():
        if key not in allow:
            unknown.append(key)
            retained[key] = _truncate(value)
    if isinstance(flags, dict):
        retained["flags"] = _truncate(flags)
    if "system" in payload:
        retained["system"] = _truncate(payload["system"])
    if unknown:
        store.warn(
            "info",
            "unmapped-fields",
            "Fields outside the pinned core schema were retained: " + ", ".join(sorted(unknown)),
            source_path,
        )
    return retained, flag_scopes


def _domains(document_type: str, embedded_counts: dict, refs: list[str]) -> list[str]:
    found = set(PRIMARY_DOMAINS.get(document_type, []))
    for embedded_type in embedded_counts:
        domain = EMBEDDED_DOMAIN.get(embedded_type)
        if domain:
            found.add(domain)
    if refs:
        found.add("assets")
    return [domain for domain in DOMAIN_ORDER if domain in found]


def _assemble_assets(store: Store, hits: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for hit in hits:
        ref = hit["ref"]
        safe, problem = _safe_ref(ref)
        kind = _kind_for_ref(ref)
        external = problem == "external-url-reference"
        hostile = problem in {"hostile-asset-reference", "rejected-zip-entry"}
        if problem:
            store.warn("warning", problem, "Asset reference was not used to read outside the package or over the network.", ref)
        present = False
        if safe and not hostile and not external:
            present = _asset_present(store, safe)
            if not present:
                store.warn("warning", "missing-asset", "Referenced file is not in the package.", ref)
        bucket = grouped.get(ref)
        pointer = {"document_type": hit["document_type"], "id": hit["id"], "field": hit["field"]}
        if bucket is None:
            grouped[ref] = {
                "ref": ref,
                "kind": "external" if external else kind,
                "present_in_package": present,
                "hostile": hostile,
                "external": external,
                "referenced_by": [pointer],
            }
        else:
            bucket["referenced_by"].append(pointer)
            bucket["present_in_package"] = bucket["present_in_package"] or present
    referenced = set(grouped)
    for name in store.files:
        kind = MEDIA_KINDS.get(Path(name).suffix.lower())
        if kind and name not in referenced and not _referenced_by_suffix_strip(name, grouped):
            grouped[name] = {
                "ref": name,
                "kind": kind,
                "present_in_package": True,
                "hostile": False,
                "external": False,
                "referenced_by": [],
            }
            store.warn("info", "unreferenced-package-file", "Package file looks like media and is not referenced by a document.", name)
    assets = list(grouped.values())
    for asset in assets:
        asset["referenced_by"] = sorted(asset["referenced_by"], key=lambda item: (item["field"], item["document_type"], item["id"] or ""))
    assets.sort(key=lambda item: item["ref"])
    return assets


def _referenced_by_suffix_strip(name: str, grouped: dict) -> bool:
    for ref in grouped:
        safe, problem = _safe_ref(ref)
        if problem or not safe:
            continue
        if safe == name:
            return True
    return False


def _asset_present(store: Store, safe: str) -> bool:
    if store.get(safe) is not None:
        return True
    for prefix in ("modules/", "worlds/", "systems/"):
        if safe.startswith(prefix):
            parts = safe.split("/", 2)
            if len(parts) == 3 and store.get(parts[2]) is not None:
                return True
    return False


def _kind_for_ref(ref: str) -> str:
    suffix = Path(ref.split("?", 1)[0]).suffix.lower()
    return MEDIA_KINDS.get(suffix, "unknown")


def _safe_ref(ref: str | None) -> tuple[str | None, str | None]:
    if ref is None:
        return None, None
    if "\x00" in ref:
        return None, "hostile-asset-reference"
    stripped = ref.strip()
    if not stripped:
        return None, None
    if "://" in stripped or stripped.startswith("data:"):
        return None, "external-url-reference"
    if stripped.startswith("/") or stripped.startswith("\\"):
        return None, "hostile-asset-reference"
    if len(stripped) >= 2 and stripped[1] == ":":
        return None, "hostile-asset-reference"
    parts: list[str] = []
    for part in stripped.replace("\\", "/").split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            return None, "hostile-asset-reference"
        parts.append(part)
    if not parts:
        return None, None
    return "/".join(parts), None


def _read_world_data(
    store: Store,
    *,
    system: str | None,
    packs: list[dict],
    documents: list[dict],
    behaviors: list[dict],
    asset_hits: list[dict],
    pinned_noted: set[str],
    seen_paths: set[str],
) -> None:
    names = set()
    for name in store.files:
        if name.startswith("data/"):
            names.add(name[len("data/"):].split("/")[0])
    for name in sorted(names):
        path = f"data/{name}"
        if path in seen_paths:
            continue
        collection_key = name if _is_dir(store, path) else Path(name).stem
        document_type = WORLD_COLLECTIONS.get(collection_key)
        if document_type is None:
            store.warn(
                "warning",
                "unknown-world-collection",
                "World data entry is not in the collection names this spike recognizes.",
                path,
            )
            document_type = "Unknown"
        record, new_docs = _read_pack(
            store,
            {"name": f"world-data:{Path(name).stem}", "label": Path(name).stem, "type": document_type, "system": system, "path": path},
            behaviors=behaviors,
            asset_hits=asset_hits,
            pinned_noted=pinned_noted,
        )
        packs.append(record)
        documents.extend(new_docs)


def _note_pack_type_rules(store: Store, packs: list[dict]) -> None:
    for pack in packs:
        document_type = pack.get("document_type")
        if document_type and document_type not in COMPENDIUM_TYPES and not str(pack.get("name") or "").startswith("world-data:"):
            store.warn(
                "info",
                "pack-type-not-in-v14-compendium-list",
                "Pack type is not in CONST.COMPENDIUM_DOCUMENT_TYPES for API version 14.",
                pack.get("path") or pack.get("name") or "",
            )
        if document_type in {"Actor", "Item", "Adventure"} and not pack.get("system"):
            store.warn(
                "info",
                "pack-missing-system",
                "Actor, Item, and Adventure packs are documented as requiring a system field since Foundry version 10.",
                pack.get("path") or "",
            )


def _counts(documents: list[dict], assets: list[dict], behaviors: list[dict], diagnostics: list[dict]) -> dict:
    by_type: dict[str, int] = {}
    embedded: dict[str, int] = {}
    domains: set[str] = set()
    for document in documents:
        by_type[document["document_type"]] = by_type.get(document["document_type"], 0) + 1
        for embedded_type, count in document["embedded_counts"].items():
            embedded[embedded_type] = embedded.get(embedded_type, 0) + count
        domains.update(document["domains"])
    by_kind: dict[str, int] = {}
    for asset in assets:
        by_kind[asset["kind"]] = by_kind.get(asset["kind"], 0) + 1
    if assets:
        domains.add("assets")
    if diagnostics:
        domains.add("diagnostics")
    domains.add("provenance")
    return {
        "documents_by_type": {key: by_type[key] for key in sorted(by_type)},
        "embedded_by_type": {key: embedded[key] for key in sorted(embedded)},
        "assets_by_kind": {key: by_kind[key] for key in sorted(by_kind)},
        "behaviors": len(behaviors),
        "diagnostics": len(diagnostics),
        "domains_present": [domain for domain in (*DOMAIN_ORDER, "provenance", "diagnostics") if domain in domains],
    }


def _sorted_diagnostics(diagnostics: list[dict]) -> list[dict]:
    rank = {"error": 0, "warning": 1, "info": 2}
    unique = []
    seen = set()
    for item in diagnostics:
        key = (item["severity"], item["code"], item["path"], item["message"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    unique.sort(key=lambda item: (rank.get(item["severity"], 9), item["code"], item["path"], item["message"]))
    return unique


def _truncate(value: object) -> object:
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    except TypeError:
        encoded = json.dumps(str(value))
    if len(encoded) <= MAX_RETAINED_CHARS:
        return json.loads(encoded)
    return {
        "_truncated": True,
        "sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        "bytes": len(encoded.encode("utf-8")),
        "preview": encoded[:500],
    }
