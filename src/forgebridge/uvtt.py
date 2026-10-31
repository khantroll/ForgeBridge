"""Write one Foundry scene as UVTT JSON, plus a graded loss report.

The scene may be a NeDB or JSON text pack, or a synthetic LevelDB pack.
The package may be a module folder or a zip of that folder. Zip entries whose
names leave the archive are not extracted and are not executed.
LevelDB values are parsed as JSON. They are not executed.

The UVTT object uses only the core fields on
https://arkenforge.com/universal-vtt-files/
read 2026-10-03. That page's dateModified is 2026-08-22.
Core fields used: format, resolution.map_origin, resolution.map_size,
resolution.pixels_per_grid, line_of_sight, objects_line_of_sight, portals
(position, bounds, rotation, closed, freestanding), environment.baked_lighting,
environment.ambient_light, top-level lights, and image.
Exact point/color shapes follow a user-supplied Arkenforge export tested 2026-10-08.
software and creator are Arkenforge extras on that page, so they are omitted.
The tested Arkenforge export uses format 1.0 and absolute {x, y} portal bounds.

Grades use that page plus the public Toolkit notes recorded in
docs/research/ARKENFORGE.md (retrieved 2026-10-03). native is a UVTT field this
file fills. approximate is in the file, or omitted, with a documented mismatch.
manual is a Toolkit UI feature with no file this slice can write. unsupported
has no documented equivalent, or the data cannot be used. No Arkenforge API is
invented.

Foundry constants used for this slice, Version 14 API, retrieved 2026-10-03:
GRID_TYPES.SQUARE is 1. WALL_DOOR_TYPES values that become portals are 1 and 2.
WALL_DOOR_STATES: CLOSED 0, OPEN 1, LOCKED 2.
Foundry light radii are stored in scene distance units; grid.distance is the number of
those units per square. UVTT range is in squares, so the outer Foundry radius is
converted by grid.distance. Separate bright/dim radii and richer rendering properties
are reported as approximations rather than silently flattened.
"""

from __future__ import annotations

import base64
import json
import io
import math
import tempfile
import zipfile
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from forgebridge.inventory import (
    MAX_ENTRIES,
    MAX_ENTRY_BYTES,
    MAX_TOTAL_BYTES,
    _package_subdir,
    _safe_ref,
    _safe_zip_name,
    inventory_path,
)
from forgebridge.leveldb import LevelDBUnavailable, read_leveldb_directory
from forgebridge.notes import correlate_notes
from forgebridge.validate import InventoryFatal

UVTT_SOURCE = "https://arkenforge.com/universal-vtt-files/"
UVTT_READ_ON = "2026-10-03"
UVTT_PAGE_MODIFIED = "2026-08-22"

NATIVE = "native"
APPROXIMATE = "approximate"
MANUAL = "manual"
UNSUPPORTED = "unsupported"

_GRADE_PREFIX = {
    NATIVE: "Native:",
    APPROXIMATE: "Approximate:",
    MANUAL: "Manual:",
    UNSUPPORTED: "Unsupported:",
}

GRID_SQUARE = 1
PORTAL_DOOR_CODES = {1, 2}
DOOR_CLOSED = 0
DOOR_OPEN = 1
DOOR_LOCKED = 2

LOOSE_IMPORT_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".mp4",
    ".m4v",
    ".webm",
    ".mp3",
    ".ogg",
    ".wav",
}
LOOSE_IMPORT_LIST = "JPG, PNG, WEBP, GIF, MP4, M4V, WEBM, MP3, OGG, and WAV"

SCENE_FIELDS_EXPLAINED = {
    "_id",
    "name",
    "width",
    "padding",
    "background",
    "dimensions",
    "height",
    "img",
    "grid",
    "thumb",
    "levels",
    "walls",
    "lights",
    "sounds",
    "tokens",
    "tiles",
    "notes",
    "regions",
    "flags",
    "environment",
    "ambient_light",
    "ambientLight",
    "tokenVision",
    "fog",
    "fogExploration",
    "globalLight",
}

RETAINED_SKIP = {
    "_id",
    "_stats",
    "effects",
    "flags",
    "folder",
    "img",
    "items",
    "name",
    "ownership",
    "pages",
    "results",
    "sort",
    "sounds",
    "system",
    "type",
}

# Public Toolkit UI, no published file. Citations are in docs/research/ARKENFORGE.md.
_MANUAL_DOCUMENT = {
    "Actor": (
        "Notes in the Toolkit can hold a 5e character stat block (v0.5.0.0, 2026-01-13). "
        "No note file format was published, so the actor is not in the UVTT file."
    ),
    "Item": (
        "Notes in the Toolkit can hold a 5e item block (v0.5.0.0, 2026-01-13). "
        "That is not a general item system, and no item file format was published."
    ),
    "JournalEntry": (
        "Notes exist in the Toolkit, including adventure templates (v0.5.0.0, 2026-01-13). "
        "Linked journal/page source data is correlated in the ForgeBridge companion. "
        "No native Arkenforge note writer is implemented."
    ),
    "RollTable": (
        "Rollable tables exist in the Toolkit (v0.5.0.0, 2026-01-13). "
        "No table file format was published."
    ),
    "Playlist": (
        "Playlists exist in the Toolkit (v0.5.0.0 and v0.5.1). "
        "MP3, OGG, and WAV can be imported as loose audio. No playlist file format was published."
    ),
    "Macro": (
        "Hotkeys can trigger content in the Toolkit (v0.5.0.0, 2026-01-13). "
        "A hotkey profile export is unspecified text. The macro was not executed."
    ),
}


def build_uvtt_slice(package: Path, scene_id: str) -> dict:
    """Return UVTT, report, full source scene, and correlated scene notes."""
    if package.is_symlink():
        raise InventoryFatal("UVTT slice does not follow a symlinked package root.")
    if package.is_file():
        if package.suffix.lower() != ".zip":
            raise InventoryFatal("UVTT slice reads a module folder or a .zip archive.")
        with tempfile.TemporaryDirectory() as tmp:
            root, rejected = _safe_extract_zip(package, Path(tmp))
            return _slice_directory(root, scene_id, rejected)
    if not package.is_dir():
        raise InventoryFatal("UVTT slice reads a module folder or a .zip archive.")
    return _slice_directory(package, scene_id, [])


def _slice_directory(package: Path, scene_id: str, rejected_zip_entries: list[str]) -> dict:
    inventory = inventory_path(package)
    scene_row = _scene_row(inventory, scene_id)
    payload = _load_scene_payload(package, scene_row, scene_id)
    uvtt, lines = _scene_to_uvtt(package, payload)
    scene_notes = _scene_notes(package, inventory, scene_row, payload)
    for note in scene_notes['notes']:
        lines.append(_line(MANUAL, 'note-journal-correlation',
            f"note {note['note_index']}, status {note['status']}. "
            "See scene_notes in the companion JSON and the .notes.txt GM reference. "
            "These preserve/correlate source data; they do not create native Arkenforge notes.",
            document_type='Note', id=note.get('note_id'), path='entryId'))
    for error in scene_notes['read_errors']:
        lines.append(_line(UNSUPPORTED, 'journal-source-read', error, document_type='JournalEntry'))
    dependencies = scene_notes['dependencies']
    if dependencies['references'] or dependencies['truncated']:
        lines.append(_line(MANUAL, 'journal-dependencies',
            f"Linked-content resolution counts: {json.dumps(dependencies['counts'], sort_keys=True)}; "
            f"traversal limited: {dependencies['truncated']}. "
            "Full referenced journal/table source objects and exact link statuses are in scene_notes.dependencies. "
            "The .notes.txt reference includes linked text and table ranges/weights; no native notes or table rolls are created.",
            document_type='JournalEntry'))
    lines.extend(_other_document_lines(inventory, scene_id))
    lines.extend(_behavior_lines(inventory))
    lines.extend(_asset_lines(inventory, _image_ref(lines), scene_id))
    lines.extend(_pack_lines(inventory))
    lines.extend(_package_file_lines(inventory))
    lines.extend(_rejected_zip_lines(rejected_zip_entries))
    report = _report(scene_id, payload.get("name"), lines)
    return {"uvtt": uvtt, "loss_report": report, "source_scene": payload, "scene_notes": scene_notes}


def _journal_pack_payloads(package: Path, row: dict) -> list[dict]:
    """Read complete source objects using the same containment and size limits."""
    safe, problem = _safe_ref(row.get('source_path'))
    if problem or not safe:
        raise InventoryFatal('journal pack path was rejected')
    storage = row.get('storage')
    if storage == 'leveldb':
        src = _package_subdir(package, safe)
        if src is None:
            raise InventoryFatal('journal pack directory was rejected')
        try:
            result = read_leveldb_directory(src, max_entries=MAX_ENTRIES, max_value_bytes=MAX_ENTRY_BYTES)
        except LevelDBUnavailable as exc:
            raise InventoryFatal(str(exc)) from exc
        if not result.opened:
            raise InventoryFatal(f'journal pack {safe} could not be opened')
        # Never silently report a partial pack as fully resolved.
        if result.diagnostics:
            raise InventoryFatal(f'journal pack {safe} has read diagnostics; inspect its inventory before correlation')
        return [p for kind, p in result.documents if kind == row.get('document_type') and isinstance(p, dict)]
    if storage not in {'json', 'nedb'}:
        raise InventoryFatal(f'journal pack {safe} has unsupported storage {storage!r}')
    path = _package_file(package, safe)
    if path.stat().st_size > MAX_ENTRY_BYTES:
        raise InventoryFatal('journal pack exceeds the read budget')
    try:
        text = path.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError) as exc:
        raise InventoryFatal(f'journal pack {safe} was not readable text') from exc
    return _payloads_json(text) if storage == 'json' else _payloads_jsonl(text)


def _scene_notes(package: Path, inventory: dict, scene_row: dict, scene: dict) -> dict:
    candidates, errors = [], []
    parent_id = _parent_adventure_id(scene_row)
    rows = []
    if parent_id:
        rows.append({**scene_row, 'document_type': 'Adventure'})
    rows.extend(row for row in inventory['documents'] if row.get('document_type') in {'JournalEntry', 'RollTable'})
    seen = set()
    if scene.get('notes'):
        for row in rows:
            key = (row.get('source_path'), row.get('document_type'))
            if key in seen:
                continue
            seen.add(key)
            try:
                payloads = _journal_pack_payloads(package, row)
            except (InventoryFatal, OSError) as exc:
                errors.append(str(exc))
                continue
            source = {'pack': row.get('pack'), 'source_path': row.get('source_path'),
                      'parent_adventure_id': parent_id if row['document_type'] == 'Adventure' else None,
                      'pack_id': None if row['document_type'] == 'Adventure' else
                          f"{inventory['provenance']['package_id']}.{row.get('pack')}"}
            if row['document_type'] == 'Adventure':
                parents = [p for p in payloads if _text_id(p) == parent_id]
                if len(parents) != 1:
                    errors.append('selected parent Adventure was missing or ambiguous during journal correlation')
                    continue
                for field, kind in [('journal', 'JournalEntry'), ('tables', 'RollTable')]:
                    objects = parents[0].get(field, [])
                    if not isinstance(objects, list):
                        errors.append(f'selected Adventure {field} collection was not an array')
                        continue
                    if any(not isinstance(obj, dict) for obj in objects):
                        errors.append(f'selected Adventure contains {field} references without full source objects')
                    candidates.extend({'document_type': kind, 'source': source, 'payload': obj, 'priority': 0}
                                      for obj in objects if isinstance(obj, dict))
            else:
                priority = 1 if row.get('pack') == scene_row.get('pack') else 2
                candidates.extend({'document_type': row['document_type'], 'source': source,
                                   'payload': obj, 'priority': priority}
                                  for obj in payloads if isinstance(obj, dict))
    size = _square_grid(scene)
    origin = _scene_origin(scene, size, [])
    return correlate_notes(scene, candidates, origin, size, errors)


def _safe_extract_zip(archive: Path, dest: Path) -> tuple[Path, list[str]]:
    """Write safe zip members under dest. Names that leave the archive are not written."""
    rejected: list[str] = []
    names: list[str] = []
    root = dest.resolve()
    try:
        zf = zipfile.ZipFile(archive)
    except zipfile.BadZipFile as exc:
        raise InventoryFatal(f"not a zip archive: {archive}") from exc
    total = 0
    with zf:
        infos = [info for info in zf.infolist() if not info.is_dir() and not info.filename.endswith("/")]
        if len(infos) > MAX_ENTRIES:
            raise InventoryFatal("zip archive has too many entries and was not extracted")
        for info in infos:
            rel, _reason = _safe_zip_name(info.filename)
            if rel is None:
                rejected.append(info.filename)
                continue
            target = root / rel
            try:
                target.resolve().relative_to(root)
            except (OSError, ValueError):
                rejected.append(info.filename)
                continue
            if info.file_size > MAX_ENTRY_BYTES or total >= MAX_TOTAL_BYTES:
                raise InventoryFatal(f"zip entry exceeds the read budget: {rel}")
            with zf.open(info, "r") as handle:
                data = handle.read(MAX_ENTRY_BYTES + 1)
            if len(data) > MAX_ENTRY_BYTES or total + len(data) > MAX_TOTAL_BYTES:
                raise InventoryFatal(f"zip entry exceeds the read budget: {rel}")
            total += len(data)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            names.append(rel)
    return _zip_module_root(root, names), rejected


def _zip_module_root(dest: Path, names: list[str]) -> Path:
    for manifest in ("module.json", "world.json", "system.json"):
        if (dest / manifest).is_file():
            return dest
    tops = {name.split("/", 1)[0] for name in names if "/" in name}
    if len(tops) == 1:
        only = dest / next(iter(tops))
        for manifest in ("module.json", "world.json", "system.json"):
            if (only / manifest).is_file():
                return only
    raise InventoryFatal("zip archive has no module.json, world.json, or system.json")


def _rejected_zip_lines(names: list[str]) -> list[dict]:
    rows = []
    for name in names:
        rows.append(
            _line(
                UNSUPPORTED,
                "rejected-zip-entry",
                (
                    f'zip entry "{name}" leaves the archive or is not a safe relative path. '
                    "It was not extracted and was not executed."
                ),
                path=name,
            )
        )
    return rows


def _scene_row(inventory: dict, scene_id: str) -> dict:
    matches = [
        doc
        for doc in inventory["documents"]
        if doc.get("document_type") == "Scene" and doc.get("id") == scene_id
    ]
    if not matches:
        raise InventoryFatal(f"scene {scene_id!r} is not in this package inventory")
    row = matches[0]
    storage = row.get("storage")
    if storage not in {"nedb", "json", "leveldb"}:
        raise InventoryFatal(
            f"scene {scene_id!r} is stored as {storage}. This slice does not decode that storage."
        )
    return row


def _load_scene_payload(package: Path, row: dict, scene_id: str) -> dict:
    if row.get("storage") == "leveldb":
        return _load_leveldb_scene(package, row, scene_id)
    source = row.get("source_path")
    safe, problem = _safe_ref(source if isinstance(source, str) else None)
    if problem or not safe:
        raise InventoryFatal("scene pack path was rejected and was not read")
    path = _package_file(package, safe)
    if path.stat().st_size > MAX_ENTRY_BYTES:
        raise InventoryFatal("scene pack exceeds the read budget and was not parsed")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise InventoryFatal(f"scene pack was not readable text: {exc}") from exc
    if row["storage"] == "json":
        payloads = _payloads_json(text)
    else:
        payloads = _payloads_jsonl(text)

    parent_id = _parent_adventure_id(row)
    if parent_id is not None:
        for payload in payloads:
            doc_id = payload.get("_id") if isinstance(payload.get("_id"), str) else None
            if doc_id == parent_id:
                scene = _embedded_adventure_scene(payload, scene_id)
                if scene is not None:
                    return scene
        raise InventoryFatal(
            f"scene {scene_id!r} was not in Adventure {parent_id!r} in {safe}"
        )

    for payload in payloads:
        doc_id = payload.get("_id") if isinstance(payload.get("_id"), str) else None
        if doc_id is None and isinstance(payload.get("id"), str):
            doc_id = payload["id"]
        if doc_id == scene_id:
            return payload
    raise InventoryFatal(f"scene {scene_id!r} was not in {safe}")


def _load_leveldb_scene(package: Path, row: dict, scene_id: str) -> dict:
    source = row.get("source_path")
    safe, problem = _safe_ref(source if isinstance(source, str) else None)
    if problem or not safe:
        raise InventoryFatal("scene pack path was rejected and was not read")
    src = _package_subdir(package, safe)
    if src is None:
        raise InventoryFatal("scene pack path was rejected and was not read")
    try:
        result = read_leveldb_directory(src, max_entries=MAX_ENTRIES, max_value_bytes=MAX_ENTRY_BYTES)
    except LevelDBUnavailable as exc:
        raise InventoryFatal(str(exc)) from exc
    if not result.opened:
        diagnostics = '; '.join(f'{code}: {message}' for _, code, message in result.diagnostics[:3])
        raise InventoryFatal(
            f"scene pack {safe} is LevelDB and was not opened. It was not read as text. "
            f"Reader diagnostics: {diagnostics or 'none supplied'}"
        )
    parent_id = _parent_adventure_id(row)
    for declared, payload in result.documents:
        if not isinstance(payload, dict):
            continue
        doc_id = payload.get("_id") if isinstance(payload.get("_id"), str) else None
        if parent_id is not None and doc_id == parent_id and declared == "Adventure":
            scene = _embedded_adventure_scene(payload, scene_id)
            if scene is not None:
                return scene
        if parent_id is None and doc_id == scene_id and declared == "Scene":
            return payload
    if parent_id is not None:
        raise InventoryFatal(
            f"scene {scene_id!r} was not in Adventure {parent_id!r} in {safe}"
        )
    raise InventoryFatal(f"scene {scene_id!r} was not in {safe}")


def _parent_adventure_id(row: dict) -> str | None:
    retained = row.get("retained_fields")
    if not isinstance(retained, dict):
        return None
    parent = retained.get("_forgebridge_parent_adventure")
    if not isinstance(parent, dict):
        return None
    value = parent.get("id")
    return value if isinstance(value, str) and value else None


def _embedded_adventure_scene(adventure: dict, scene_id: str) -> dict | None:
    scenes = adventure.get("scenes")
    if not isinstance(scenes, list):
        return None
    for scene in scenes:
        if not isinstance(scene, dict):
            continue
        doc_id = scene.get("_id") if isinstance(scene.get("_id"), str) else None
        if doc_id is None and isinstance(scene.get("id"), str):
            doc_id = scene["id"]
        if doc_id == scene_id:
            return scene
    return None


def _payloads_json(text: str) -> list[dict]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InventoryFatal("scene pack JSON was not parsed as a document") from exc
    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    raise InventoryFatal("scene pack JSON was not an object or array")


def _payloads_jsonl(text: str) -> list[dict]:
    payloads = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InventoryFatal("a scene pack line was not JSON and was not executed") from exc
        if isinstance(parsed, dict):
            payloads.append(parsed)
    return payloads


def _scene_to_uvtt(package: Path, scene: dict) -> tuple[dict, list[dict]]:
    lines: list[dict] = []
    size = _square_grid(scene)
    image_ref, image_bytes = _scene_image(package, scene)
    _grade_scene_fields(scene, image_ref, lines)
    walls = scene.get("walls") if isinstance(scene.get("walls"), list) else []
    lights = scene.get("lights") if isinstance(scene.get("lights"), list) else []
    origin = _scene_origin(scene, size, lines)
    line_of_sight, portals = _walls_to_uvtt(walls, size, lines, origin)
    uvtt_lights = _lights_to_uvtt(lights, scene, size, lines, origin)
    ambient_light = _ambient_light(scene, lines)
    width = _number(scene.get("width"))
    height = _number(scene.get("height"))
    if width is None or height is None or width <= 0 or height <= 0:
        raise InventoryFatal("scene width and height must be positive numbers")
    lines.append(
        _line(
            NATIVE,
            "resolution",
            (
                f"grid { _plain(width) } by { _plain(height) } pixels at "
                f"{ _plain(size) } pixels per square, as map_size "
                f"{ _plain(width / size) } by { _plain(height / size) } and map_origin 0, 0."
            ),
            document_type="Scene",
            id=scene.get("_id") if isinstance(scene.get("_id"), str) else None,
            name=scene.get("name") if isinstance(scene.get("name"), str) else None,
            path=image_ref,
        )
    )
    lines.append(
        _line(
            NATIVE,
            "image",
            (
                f"image {image_ref} from the level background, once, as base64. "
                "Scene img was not written again when it pointed at the same file."
            ),
            document_type="Scene",
            id=_text_id(scene),
            name=_text_name(scene),
            path=image_ref,
        )
    )
    lines.append(
        _line(
            NATIVE,
            "baked-lighting",
            "environment.baked_lighting false enables imported dynamic lights; this does not remove illumination already painted into the background.",
            document_type="Scene",
            id=_text_id(scene),
            name=_text_name(scene),
            path=image_ref,
        )
    )
    lines.append(_line(NATIVE, "arkenforge-wire-shape",
        "format 1.0, named x/y points, absolute portal bounds, and top-level lights "
        "match the user-supplied Arkenforge export and the successful 2026-10-08 import test."))
    lines.append(
        _line(
            APPROXIMATE,
            "freestanding-undefined",
            (
                "freestanding is a documented bool. The UVTT page, read "
                f"{UVTT_READ_ON}, does not define it. This slice sets it false because the portal is a wall segment."
            ),
            path=UVTT_SOURCE,
        )
    )
    lines.append(
        _line(
            APPROXIMATE,
            "software-creator-not-core",
            (
                "the UVTT page says Arkenforge writes software and creator as its own extra tags. "
                "They are outside the core list, so this slice omits both."
            ),
            path=UVTT_SOURCE,
        )
    )
    uvtt = {
        "format": 1.0,
        "resolution": {
            "map_origin": {"x": 0, "y": 0},
            "map_size": {"x": _coord(width / size), "y": _coord(height / size)},
            "pixels_per_grid": int(size),
        },
        "line_of_sight": line_of_sight,
        "objects_line_of_sight": [],
        "portals": portals,
        "environment": {
            "baked_lighting": False,
            **({"ambient_light": ambient_light} if ambient_light is not None else {}),
        },
        "lights": uvtt_lights,
        "image": base64.b64encode(image_bytes).decode("ascii"),
    }
    return uvtt, lines


def _square_grid(scene: dict) -> float:
    grid = scene.get("grid")
    if not isinstance(grid, dict):
        raise InventoryFatal("scene has no grid object. UVTT map_size is in squares.")
    grid_type = grid.get("type")
    if isinstance(grid_type, bool) or grid_type != GRID_SQUARE:
        shown = grid_type if not isinstance(grid_type, bool) else "boolean"
        raise InventoryFatal(
            f"scene grid type {shown} is not GRID_TYPES.SQUARE (1). "
            "UVTT map_size is in squares, so this slice does not write a UVTT file for it."
        )
    size = _number(grid.get("size"))
    if size is None or size <= 0:
        raise InventoryFatal("scene grid size must be a positive number of pixels per square")
    return size


def _scene_image(package: Path, scene: dict) -> tuple[str, bytes]:
    ref = _background_ref(scene)
    if ref is None:
        raise InventoryFatal("scene has no level background image to place in UVTT image")
    safe, data = _read_image(package, ref)
    return safe, data


def _background_ref(scene: dict) -> str | None:
    levels = scene.get("levels")
    if isinstance(levels, list):
        for level in levels:
            if not isinstance(level, dict):
                continue
            background = level.get("background")
            if isinstance(background, dict) and isinstance(background.get("src"), str) and background["src"].strip():
                return background["src"]
    background = scene.get("background")
    if isinstance(background, dict) and isinstance(background.get("src"), str) and background["src"].strip():
        return background["src"]
    img = scene.get("img")
    if isinstance(img, str) and img.strip():
        return img
    return None


def _read_image(package: Path, ref: str) -> tuple[str, bytes]:
    safe, problem = _safe_ref(ref)
    if problem or not safe:
        raise InventoryFatal(f"UVTT image reference was rejected and not opened: {ref}")
    suffix = Path(safe).suffix.lower()
    if suffix not in {".png", ".webp"}:
        raise InventoryFatal(f"UVTT image must be PNG or WEBP: {ref}")
    path = _package_file(package, safe)
    if path.stat().st_size > MAX_ENTRY_BYTES:
        raise InventoryFatal(f"UVTT image exceeds the read budget: {ref}")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise InventoryFatal(f"UVTT image was not readable: {exc}") from exc
    if suffix == ".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise InventoryFatal(f"UVTT image is not a PNG: {ref}")
    if suffix == ".webp" and not (len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP"):
        raise InventoryFatal(f"UVTT image is not a WEBP: {ref}")
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            if image.width > 16000 or image.height > 16000:
                raise InventoryFatal(f"UVTT background exceeds Arkenforge's 16000 pixel limit: {ref}")
            # Preserve already compatible PNGs; convert WEBP and palette/grayscale images.
            if image.format != "PNG" or image.mode not in {"RGB", "RGBA"}:
                output = io.BytesIO()
                image.convert("RGBA").save(output, format="PNG")
                data = output.getvalue()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise InventoryFatal(f"UVTT image could not be decoded: {ref}: {exc}") from exc
    return safe, data


def _scene_origin(scene: dict, size: float, lines: list[dict]) -> tuple[float, float]:
    """Normalize canvas coordinates to the unpadded scene/background rectangle."""
    dimensions = scene.get("dimensions")
    explicit = isinstance(dimensions, dict) and all(_number(dimensions.get(k)) is not None for k in ("sceneX", "sceneY"))
    if explicit:
        x, y = float(dimensions["sceneX"]), float(dimensions["sceneY"])
    else:
        padding = _number(scene.get("padding", 0))
        width, height = _number(scene.get("width")), _number(scene.get("height"))
        if padding is None or padding < 0 or width is None or height is None:
            raise InventoryFatal("scene padding and dimensions must be finite non-negative numbers")
        x = math.ceil(width * padding / size) * size
        y = math.ceil(height * padding / size) * size
    background = scene.get("background")
    if isinstance(background, dict):
        for key in ("offsetX", "offsetY", "rotation", "scaleX", "scaleY"):
            if key in background:
                value = _number(background[key])
                if value is None:
                    raise InventoryFatal(f"background.{key} must be a finite number")
                if key in {"rotation", "scaleX", "scaleY"} and value != (0 if key == "rotation" else 1):
                    raise InventoryFatal(f"background.{key} transformation is not yet supported; refusing misaligned UVTT")
        x += background.get("offsetX", 0)
        y += background.get("offsetY", 0)
    lines.append(_line(NATIVE if explicit else APPROXIMATE, "coordinate-origin",
        f"Subtract canvas background origin {_plain(x)}, {_plain(y)} pixels from all walls, portals, and lights. "
        + ("Uses stored sceneX/sceneY." if explicit else "Uses padding rounded up to whole grid spaces; absent padding assumes zero. Confirm against the source scene."),
        document_type="Scene", id=_text_id(scene), path="padding"))
    return x, y


def _package_file(package: Path, safe: str) -> Path:
    root = package.resolve()
    candidates = [safe]
    parts = safe.split("/")
    if (
        len(parts) >= 3
        and parts[0] in {"modules", "worlds", "systems"}
        and parts[1] == package.name
    ):
        candidates.append("/".join(parts[2:]))

    for candidate in candidates:
        path = package / candidate
        current = path
        unsafe = False
        while True:
            if current.is_symlink():
                unsafe = True
                break
            if current.resolve() == root or current == package:
                break
            parent = current.parent
            if parent == current:
                break
            current = parent
        if unsafe:
            continue
        if _contained(root, path) and path.is_file():
            return path
    raise InventoryFatal(f"path is not a file inside the package: {safe}")


def _contained(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except (OSError, ValueError):
        return False
    return True


def _grade_scene_fields(scene: dict, image_ref: str, lines: list[dict]) -> None:
    scene_id = _text_id(scene)
    scene_name = _text_name(scene)
    if scene_name:
        lines.append(
            _line(
                MANUAL,
                "scene-name",
                (
                    f'scene name "{scene_name}". The UVTT core fields have no name. '
                    "Renaming a map is a Toolkit UI action, and no import field for the scene name was found."
                ),
                document_type="Scene",
                id=scene_id,
                name=scene_name,
            )
        )
    grid = scene.get("grid") if isinstance(scene.get("grid"), dict) else {}
    if "distance" in grid or "units" in grid:
        distance = grid.get("distance")
        units = grid.get("units")
        lines.append(
            _line(
                APPROXIMATE,
                "grid-distance",
                (
                    f"grid distance {distance} units {units!r}. "
                    "UVTT resolution has map_origin, map_size, and pixels_per_grid. "
                    "Distance and units are not those fields. The square size is still written."
                ),
                document_type="Scene",
                id=scene_id,
                name=scene_name,
                path="grid",
            )
        )
    thumb = scene.get("thumb")
    if isinstance(thumb, str) and thumb.strip():
        lines.append(
            _line(
                APPROXIMATE,
                "scene-thumb",
                (
                    f'scene thumb "{thumb}". UVTT is one image, taken from the level background, '
                    "so the thumbnail was not written a second time."
                ),
                document_type="Scene",
                id=scene_id,
                name=scene_name,
                path=thumb,
            )
        )
    img = scene.get("img")
    if isinstance(img, str) and img.strip() and img != image_ref:
        lines.append(
            _line(
                APPROXIMATE,
                "scene-img-not-chosen",
                (
                    f'scene img "{img}". The UVTT image is the level background "{image_ref}". '
                    "A second map image is not a UVTT field."
                ),
                document_type="Scene",
                id=scene_id,
                name=scene_name,
                path=img,
            )
        )
    levels = scene.get("levels") if isinstance(scene.get("levels"), list) else []
    for level in levels:
        if not isinstance(level, dict):
            continue
        level_name = level.get("name") if isinstance(level.get("name"), str) else None
        level_id = level.get("_id") if isinstance(level.get("_id"), str) else None
        label = f'"{level_name}"' if level_name else "level"
        ident = f" ({level_id})" if level_id else ""
        lines.append(
            _line(
                MANUAL,
                "level-not-image",
                (
                    f"level {label}{ident}. Only the background image is a UVTT field. "
                    "Level names are edited in the Toolkit UI, and no import field for the level name was found."
                ),
                document_type="Level",
                id=level_id,
                name=level_name,
            )
        )
    _grade_fog_vision(scene, lines)
    _grade_placeables(scene, lines)
    flags = scene.get("flags")
    if isinstance(flags, dict):
        for scope in flags:
            lines.append(
                _line(
                    UNSUPPORTED,
                    "scene-flags",
                    f'scene flags "{scope}". No documented Arkenforge flags field was found.',
                    document_type="Scene",
                    id=scene_id,
                    name=scene_name,
                    path=f"flags.{scope}",
                )
            )
    for key in scene:
        if key in SCENE_FIELDS_EXPLAINED:
            continue
        lines.append(
            _line(
                UNSUPPORTED,
                "scene-field",
                (
                    f'scene field "{key}". No documented Arkenforge field matches this name, '
                    "and the value was not copied."
                ),
                document_type="Scene",
                id=scene_id,
                name=scene_name,
                path=key,
            )
        )


def _fog_vision_settings(scene: dict) -> dict:
    """Read Foundry fog/vision switches across v10 (flat) and v11+ (nested) shapes."""
    fog = scene.get("fog") if isinstance(scene.get("fog"), dict) else {}
    environment = scene.get("environment") if isinstance(scene.get("environment"), dict) else {}
    global_light = environment.get("globalLight")
    settings = {}
    if isinstance(scene.get("tokenVision"), bool):
        settings["tokenVision"] = scene["tokenVision"]
    if isinstance(fog.get("exploration"), bool):
        settings["fog.exploration"] = fog["exploration"]
    elif isinstance(scene.get("fogExploration"), bool):
        settings["fogExploration"] = scene["fogExploration"]
    if isinstance(global_light, dict) and isinstance(global_light.get("enabled"), bool):
        settings["environment.globalLight.enabled"] = global_light["enabled"]
    elif isinstance(scene.get("globalLight"), bool):
        settings["globalLight"] = scene["globalLight"]
    return settings


def _grade_fog_vision(scene: dict, lines: list[dict]) -> None:
    """Explain source fog/vision so a fogged Toolkit player view is expected, not a defect.

    ForgeBridge does not write Toolkit fog state, explored areas or per-token
    vision. Arkenforge manual fog starts with nothing revealed for players.
    """
    settings = _fog_vision_settings(scene)
    has_fog_data = any(k in scene for k in ("tokenVision", "fog", "fogExploration", "globalLight"))
    if not settings and not has_fog_data:
        return
    vision = settings.get("tokenVision")
    exploration = settings.get("fog.exploration", settings.get("fogExploration"))
    observed = ", ".join(f"{k}={str(v).lower()}" for k, v in settings.items()) or "no readable switches"
    if vision is False:
        intent = ("In Foundry players were not limited by token vision, so the whole lit scene was visible. "
                  "To match, disable Arkenforge fog of war for this map (Live Play/VTT -> Fog of War) "
                  "or clear all fog; otherwise players see only fog.")
    elif vision is True:
        intent = ("In Foundry players saw only what their tokens could see"
                  + (", and explored areas stayed revealed" if exploration else "")
                  + ". Arkenforge manual fog starts fully covered: reveal areas as the party explores, "
                  "or enable dynamic fog if the map's tokens are set up for it.")
    else:
        intent = ("Foundry vision settings could not be read. Check Arkenforge fog of war before showing "
                  "the player screen; covered manual fog shows players only fog.")
    lines.append(_line(MANUAL, "fog-vision",
        f"scene fog/vision settings ({observed}). {intent} Foundry explored-fog history "
        "(FogExploration documents) and per-token vision are not converted.",
        document_type="Scene", id=_text_id(scene), name=_text_name(scene), path="fog"))


def _grade_placeables(scene: dict, lines: list[dict]) -> None:
    for token in _dicts(scene.get("tokens")):
        name = _text_name(token)
        label = f'"{name}"' if name else "token"
        lines.append(
            _line(
                MANUAL,
                "token",
                (
                    f"token {label} ({_text_id(token) or 'no id'}). "
                    "The UVTT page says the file cannot contain individually selectable tokens. "
                    "Tokens exist in the Toolkit UI (v0.5.0.0, 2026-01-13). "
                    "No token file format was published. It was not written to objects_line_of_sight."
                ),
                document_type="Token",
                id=_text_id(token),
                name=name,
            )
        )
    for tile in _dicts(scene.get("tiles")):
        src = _texture_src(tile)
        _safe, problem = _safe_ref(src)
        if problem:
            lines.append(
                _line(
                    UNSUPPORTED,
                    "tile",
                    (
                        f'tile "{_text_id(tile) or "no id"}" texture "{src}". '
                        "The path was not opened. UVTT cannot carry a separate map image."
                    ),
                    document_type="Tile",
                    id=_text_id(tile),
                    path=src,
                )
            )
            continue
        lines.append(
            _line(
                MANUAL,
                "tile",
                (
                    f'tile "{_text_id(tile) or "no id"}" texture "{src}". '
                    "The file stays in the package. UVTT cannot carry a second selectable image. "
                    "Loose image import exists, and no tile file format was published."
                ),
                document_type="Tile",
                id=_text_id(tile),
                path=src,
            )
        )
    for sound in _dicts(scene.get("sounds")):
        path = sound.get("path") if isinstance(sound.get("path"), str) else None
        lines.append(
            _line(
                MANUAL,
                "ambient-sound",
                (
                    f'ambient sound "{_text_id(sound) or "no id"}" path "{path}". '
                    "MP3, OGG, and WAV are confirmed loose imports. "
                    "UVTT has no audio field, and no playlist file format was published."
                ),
                document_type="AmbientSound",
                id=_text_id(sound),
                path=path,
            )
        )
    for note in _dicts(scene.get("notes")):
        lines.append(
            _line(
                MANUAL,
                "note",
                (
                    f'note "{_text_id(note) or "no id"}". '
                    "Notes exist in the Toolkit UI (v0.5.0.0, 2026-01-13). "
                    "UVTT has no notes field, no note file format was published, and the note text was not copied."
                ),
                document_type="Note",
                id=_text_id(note),
                name=_text_name(note),
            )
        )
    for region in _dicts(scene.get("regions")):
        name = _text_name(region)
        label = f'"{name}"' if name else "region"
        lines.append(
            _line(
                UNSUPPORTED,
                "region",
                (
                    f"region {label} ({_text_id(region) or 'no id'}). "
                    "Regions are not a documented user-scriptable system, and its behaviors were not executed."
                ),
                document_type="Region",
                id=_text_id(region),
                name=name,
            )
        )


def _walls_to_uvtt(walls: list, size: float, lines: list[dict], origin: tuple[float, float] = (0, 0)) -> tuple[list, list]:
    line_of_sight = []
    portals = []
    for wall in walls:
        if not isinstance(wall, dict):
            continue
        segment = _segment(wall.get("c"), size)
        wall_id = _text_id(wall)
        if segment is None:
            lines.append(
                _line(
                    UNSUPPORTED,
                    "wall-geometry",
                    (
                        f'wall "{wall_id or "no id"}" has no 4-number coordinate list, '
                        "so no UVTT segment was written."
                    ),
                    document_type="Wall",
                    id=wall_id,
                    path="c",
                )
            )
            continue
        (x1, y1), (x2, y2) = segment
        ox, oy = origin[0] / size, origin[1] / size
        x1, y1, x2, y2 = x1 - ox, y1 - oy, x2 - ox, y2 - oy
        door = wall.get("door")
        if isinstance(door, int) and not isinstance(door, bool) and door in PORTAL_DOOR_CODES:
            closed, state_line = _portal_closed(wall.get("ds"), wall_id)
            if state_line is not None:
                lines.append(state_line)
            lines.append(
                _line(
                    APPROXIMATE,
                    "door-type",
                    (
                        f'wall "{wall_id or "no id"}" door code {door}. '
                        "UVTT portals have no door-type field. The segment was written as a portal."
                    ),
                    document_type="Wall",
                    id=wall_id,
                    path="door",
                )
            )
            portals.append({
                # The native Arkenforge exporter stores unsigned endpoint deltas here.
                "position": {"x": _coord(abs(x2 - x1)), "y": _coord(abs(y2 - y1))},
                "bounds": [{"x": _coord(x1), "y": _coord(y1)}, {"x": _coord(x2), "y": _coord(y2)}],
                "rotation": 0,
                "closed": closed,
                "freestanding": False,
            })
            restrictions = {key: wall.get(key) for key in ("light", "sight", "move", "sound", "dir", "threshold") if key in wall}
            blocking_instructions = []
            for key, label in (("light", "Light"), ("sight", "Vision")):
                if wall.get(key) == 0:
                    blocking_instructions.append(f"Source {key}=0: leave Blocks {label} disabled, including when closed.")
                elif wall.get(key) == 20:
                    blocking_instructions.append(f"Source {key}=20: enable Blocks {label} for the closed state.")
                else:
                    blocking_instructions.append(f"Inspect the source {key} restriction before setting Blocks {label}.")
            lines.append(_line(MANUAL, "portal-blocking-properties",
                f'portal {len(portals)-1}, wall "{wall_id or "no id"}": source restrictions {json.dumps(restrictions, sort_keys=True)}, ds={wall.get("ds")!r}. '
                "UVTT closed preserves the initial door state but cannot separately encode Arkenforge Blocks Light/Blocks Vision and toggle state. "
                "Review the intended blocking capabilities in Customise -> Blocking after import. "
                + " ".join(blocking_instructions) + " "
                "Full source settings are preserved in the source scene sidecar; do not enable light blocking on transparent windows indiscriminately.",
                document_type="Wall", id=wall_id, path="light"))
            lines.append(
                _line(
                    NATIVE,
                    "portal",
                    (
                        f'wall "{wall_id or "no id"}" as a portal. '
                        f"closed is {str(closed).lower()} from door state {wall.get('ds')} "
                        "(CLOSED is 0, OPEN is 1). A locked state is not a separate UVTT value."
                    ),
                    document_type="Wall",
                    id=wall_id,
                    path="c",
                )
            )
            continue
        restrictions = {key: wall.get(key) for key in ("light", "sight", "move", "sound", "dir", "threshold") if key in wall}
        bounds = [{"x": _coord(x1), "y": _coord(y1)}, {"x": _coord(x2), "y": _coord(y2)}]
        # UVTT LOS cannot represent a movement-only wall without inventing an
        # opaque light/vision barrier. Keep its complete source in the sidecar.
        if wall.get("light") == 0 and wall.get("sight") == 0:
            lines.append(_line(MANUAL, "wall-transparent-omitted",
                f'wall "{wall_id or "no id"}", bounds {json.dumps(bounds, sort_keys=True)}: '
                f'source restrictions {json.dumps(restrictions, sort_keys=True)}. '
                "Source light=0 and sight=0: omitted from UVTT line_of_sight so it does not become opaque. "
                "If needed, recreate its movement/sound blocking separately in Arkenforge; leave Blocks Light and Blocks Vision disabled. "
                "The complete source wall remains in the source scene sidecar.",
                document_type="Wall", id=wall_id, path="c"))
            continue
        segment_index = len(line_of_sight)
        line_of_sight.append(bounds)
        threshold = wall.get("threshold")
        has_threshold = (
            any(value is not None and value is not False for value in threshold.values())
            if isinstance(threshold, dict) else threshold is not None and threshold is not False
        )
        simple_optical_wall = (
            wall.get("light") == 20 and wall.get("sight") == 20
            and wall.get("dir", 0) == 0 and not has_threshold
        )
        if not simple_optical_wall:
            instructions = []
            for key, label in (("light", "Light"), ("sight", "Vision")):
                if wall.get(key) == 0:
                    instructions.append(f"Source {key}=0: disable Blocks {label}.")
                elif wall.get(key) == 20:
                    instructions.append(f"Source {key}=20: enable Blocks {label}.")
                else:
                    instructions.append(f"Source {key}={wall.get(key)!r}: inspect this restriction; it is not equivalent to a simple on/off setting.")
            lines.append(_line(MANUAL, "wall-blocking-properties",
                f'line_of_sight {segment_index}, wall "{wall_id or "no id"}", bounds {json.dumps(bounds, sort_keys=True)}: '
                f'source restrictions {json.dumps(restrictions, sort_keys=True)}. '
                "UVTT retains this segment's geometry but cannot independently encode its light/vision modes, direction, or thresholds. "
                "After import review Customise -> Blocking. " + " ".join(instructions) + " "
                "Movement/sound restrictions also require review; complete source settings remain in the sidecar.",
                document_type="Wall", id=wall_id, path="light"))
        lines.append(
            _line(
                NATIVE if simple_optical_wall else APPROXIMATE,
                "line-of-sight",
                (
                    f'wall "{wall_id or "no id"}" as one line_of_sight segment. '
                    f"Door code {door!r} is not a portal."
                ),
                document_type="Wall",
                id=wall_id,
                path="c",
            )
        )
    if not line_of_sight:
        lines.append(
            _line(
                NATIVE,
                "line-of-sight-empty",
                "line_of_sight is empty. Door walls use portals; walls explicitly transparent to both light and vision are omitted.",
                document_type="Wall",
            )
        )
    return line_of_sight, portals


def _portal_closed(ds: object, wall_id: str | None) -> tuple[bool, dict | None]:
    if ds == DOOR_OPEN:
        return False, None
    if ds == DOOR_LOCKED:
        return True, _line(
            APPROXIMATE,
            "door-locked",
            (
                f'wall "{wall_id or "no id"}" door state LOCKED (2). '
                "UVTT closed is only a bool, so the portal is closed and the locked state was left out."
            ),
            document_type="Wall",
            id=wall_id,
            path="ds",
        )
    if ds == DOOR_CLOSED:
        return True, None
    return True, _line(
        APPROXIMATE,
        "door-state",
        (
            f'wall "{wall_id or "no id"}" door state {ds!r} is outside CLOSED 0, OPEN 1, and LOCKED 2. '
            "The portal was written closed."
        ),
        document_type="Wall",
        id=wall_id,
        path="ds",
    )


def _ambient_light(scene: dict, lines: list[dict]) -> str | None:
    """Return a directly stored scene ambient hex color when one is available."""
    environment = scene.get("environment")
    candidates = []
    if isinstance(environment, dict):
        for key in ("ambient_light", "ambientLight"):
            value = environment.get(key)
            if isinstance(value, str):
                candidates.append((f"environment.{key}", value))
    for key in ("ambient_light", "ambientLight"):
        value = scene.get(key)
        if isinstance(value, str):
            candidates.append((key, value))
    for path, color in candidates:
        if _hex_color(color):
            lines.append(_line(NATIVE, "ambient-light",
                f"scene ambient color {color} as UVTT environment.ambient_light.",
                document_type="Scene", id=_text_id(scene), name=_text_name(scene), path=path))
            return color
        lines.append(_line(UNSUPPORTED, "ambient-light-invalid",
            f"scene ambient color {color!r} is not a hex color and was not written.",
            document_type="Scene", id=_text_id(scene), name=_text_name(scene), path=path))
    if isinstance(environment, dict) and environment:
        lines.append(_line(APPROXIMATE, "foundry-environment",
            "Foundry scene environment data is richer than UVTT ambient_light. No ambient hex color was stored directly, so ForgeBridge did not invent one from darknessLevel, base/dark hue, luminosity, saturation, shadows, or globalLight.",
            document_type="Scene", id=_text_id(scene), name=_text_name(scene), path="environment"))
    return None


def _lights_to_uvtt(lights: list, scene: dict, size: float, lines: list[dict], origin: tuple[float, float] = (0, 0)) -> list[dict]:
    written = []
    grid = scene.get("grid") if isinstance(scene.get("grid"), dict) else {}
    grid_distance = _number(grid.get("distance"))
    for light in lights:
        if not isinstance(light, dict):
            continue
        light_id = _text_id(light)
        config = light.get("config") if isinstance(light.get("config"), dict) else {}
        raw_color = config.get("color")
        untinted = raw_color is None or (isinstance(raw_color, str) and not raw_color.strip())
        color = "#ffffff" if untinted else raw_color
        x, y = _number(light.get("x")), _number(light.get("y"))
        dim, bright = _number(config.get("dim")), _number(config.get("bright"))
        if x is None or y is None:
            lines.append(_line(UNSUPPORTED, "light-not-written",
                f'light "{light_id or "no id"}" has missing or invalid x/y coordinates, so no UVTT light was written.',
                document_type="AmbientLight", id=light_id))
            continue
        if not _hex_color(color):
            lines.append(_line(UNSUPPORTED, "light-not-written",
                f'light "{light_id or "no id"}" has invalid non-empty color {raw_color!r}, so no UVTT light was written.',
                document_type="AmbientLight", id=light_id, path="config.color"))
            continue
        if untinted:
            lines.append(_line(APPROXIMATE, "light-untinted",
                f'light "{light_id or "no id"}" has an unset tint, which is a valid Foundry light. '
                "Represented as neutral white in UVTT rather than discarded. The original unset value and animation are preserved in source_scene.",
                document_type="AmbientLight", id=light_id, path="config.color"))
        digits = color[1:]
        if len(digits) == 3:
            digits = "".join(char * 2 for char in digits)
        out = {"position": {"x": _coord((x - origin[0]) / size), "y": _coord((y - origin[1]) / size)},
               "color": "ff" + digits, "intensity": 0.5, "shadows": True}
        lines.append(_line(APPROXIMATE, "light-import-defaults",
            f'light "{light_id or "no id"}": opaque ARGB color, intensity 0.5, shadows true match the working Arkenforge test. '
            "These are compatibility defaults, not equivalent Foundry luminosity or numeric shadows; full source config is preserved in the sidecar.",
            document_type="AmbientLight", id=light_id, path="config"))
        radii = [value for value in (dim, bright) if value is not None]
        if any(value < 0 for value in radii):
            lines.append(_line(UNSUPPORTED, "darkness-source",
                f'light "{light_id or "no id"}" has negative dim/bright radius {config.get("dim")!r}/{config.get("bright")!r}. Foundry uses negative light radii for darkness/blackness; UVTT documents a light range but no darkness-source equivalent. Range was not written.',
                document_type="AmbientLight", id=light_id, path="config"))
        elif radii and grid_distance is not None and grid_distance > 0:
            outer = max(radii)
            out["range"] = _coord(outer / grid_distance)
            lines.append(_line(NATIVE, "light-range",
                f'light "{light_id or "no id"}" outer radius {_plain(outer)} distance units at {_plain(grid_distance)} units per square as UVTT range {_plain(outer / grid_distance)} squares.',
                document_type="AmbientLight", id=light_id, path="config.dim"))
            if dim is not None and bright is not None and dim != bright:
                lines.append(_line(APPROXIMATE, "light-bright-radius",
                    f'light "{light_id or "no id"}" has separate Foundry dim/bright radii {_plain(dim)}/{_plain(bright)}. UVTT has one range, so only the outer radius is represented.',
                    document_type="AmbientLight", id=light_id, path="config.bright"))
        elif radii:
            lines.append(_line(APPROXIMATE, "light-range-no-grid-distance",
                f'light "{light_id or "no id"}" has dim/bright radii {config.get("dim")!r}/{config.get("bright")!r}, but the scene grid has no positive distance-units-per-square value. UVTT range is in squares, so ForgeBridge did not guess a conversion.',
                document_type="AmbientLight", id=light_id, path="grid.distance"))
        richer = [key for key in ("alpha","angle","animation","attenuation","coloration","contrast","darkness","luminosity","saturation","shadows") if key in config]
        if richer:
            lines.append(_line(APPROXIMATE, "light-rendering-properties",
                f'light "{light_id or "no id"}" Foundry rendering properties {", ".join(richer)} were not mapped to UVTT intensity/shadows because the formats do not document equivalent semantics.',
                document_type="AmbientLight", id=light_id, path="config"))
        written.append(out)
        lines.append(_line(NATIVE, "light",
            f'light "{light_id or "no id"}" position and color {color}' + (f", range {out['range']} squares." if "range" in out else " only."),
            document_type="AmbientLight", id=light_id, path="config.color"))
    return written

def _other_document_lines(inventory: dict, scene_id: str) -> list[dict]:
    rows = []
    for doc in inventory["documents"]:
        if doc.get("document_type") == "Scene" and doc.get("id") == scene_id:
            continue
        dtype = doc.get("document_type") or "Unknown"
        name = doc.get("name") if isinstance(doc.get("name"), str) else None
        doc_id = doc.get("id") if isinstance(doc.get("id"), str) else None
        label = f'"{name}"' if name else "(unnamed)"
        ident = f" ({doc_id})" if doc_id else ""
        if dtype in _MANUAL_DOCUMENT:
            grade = MANUAL
            why = _MANUAL_DOCUMENT[dtype]
        else:
            grade = UNSUPPORTED
            why = "No documented Arkenforge file or UI equivalent was found for this document type."
        rows.append(
            _line(
                grade,
                "document-not-in-uvtt",
                f"{dtype} {label}{ident}. {why}",
                document_type=dtype,
                id=doc_id,
                name=name,
                path=doc.get("source_path") if isinstance(doc.get("source_path"), str) else None,
            )
        )
        rows.extend(_retained_field_lines(doc))
    return rows


def _retained_field_lines(doc: dict) -> list[dict]:
    retained = doc.get("retained_fields")
    if not isinstance(retained, dict):
        return []
    source = retained.get("_unpinned_source")
    keys = list(source) if isinstance(source, dict) else list(retained)
    rows = []
    for key in keys:
        if key in RETAINED_SKIP or key == "_unpinned_source":
            continue
        rows.append(
            _line(
                UNSUPPORTED,
                "retained-field",
                (
                    f'field "{key}" on {doc.get("document_type")} '
                    f'"{doc.get("name")}" ({doc.get("id")}). '
                    "No documented Arkenforge field matches it, and the value was not copied."
                ),
                document_type=doc.get("document_type") if isinstance(doc.get("document_type"), str) else None,
                id=doc.get("id") if isinstance(doc.get("id"), str) else None,
                name=doc.get("name") if isinstance(doc.get("name"), str) else None,
                path=key,
            )
        )
    return rows


def _behavior_lines(inventory: dict) -> list[dict]:
    rows = []
    for behavior in inventory["behaviors"]:
        kind = behavior.get("kind") if isinstance(behavior.get("kind"), str) else "behavior"
        name = behavior.get("name") if isinstance(behavior.get("name"), str) else None
        label = f'"{name}"' if name else kind
        if kind == "macro":
            grade = MANUAL
            summary = (
                f"{kind} {label} maps to a Toolkit hotkey (v0.5.0.0, 2026-01-13). "
                "The macro was not executed, and the hotkey text format is unpublished."
            )
        else:
            grade = UNSUPPORTED
            summary = (
                f"{kind} {label} was not executed. "
                "No documented Arkenforge equivalent was found."
            )
        rows.append(
            _line(
                grade,
                "behavior-not-executed",
                summary,
                document_type=kind,
                id=behavior.get("id") if isinstance(behavior.get("id"), str) else None,
                name=name,
                path=behavior.get("source_path") if isinstance(behavior.get("source_path"), str) else None,
            )
        )
    return rows


def scene_loose_files(package: Path, scene_id: str) -> list[tuple[str, bytes]]:
    """Return (basename, bytes) for scene image and audio files the import list allows."""
    if package.is_symlink():
        raise InventoryFatal("UVTT slice does not follow a symlinked package root.")
    if package.is_file():
        if package.suffix.lower() != ".zip":
            raise InventoryFatal("UVTT slice reads a module folder or a .zip archive.")
        with tempfile.TemporaryDirectory() as tmp:
            root, _rejected = _safe_extract_zip(package, Path(tmp))
            return _loose_files_in_directory(root, scene_id)
    if not package.is_dir():
        raise InventoryFatal("UVTT slice reads a module folder or a .zip archive.")
    return _loose_files_in_directory(package, scene_id)


def _loose_files_in_directory(package: Path, scene_id: str) -> list[tuple[str, bytes]]:
    inventory = inventory_path(package)
    files: list[tuple[str, bytes]] = []
    seen: set[str] = set()
    for asset in inventory["assets"]:
        if _scene_asset_action(asset, scene_id) != "copy":
            continue
        ref = asset.get("ref")
        if not isinstance(ref, str):
            continue
        safe, problem = _safe_ref(ref)
        if problem or not safe:
            continue
        name = Path(safe).name
        if not name or name in seen or name in {".", ".."} or "/" in name or "\\" in name:
            continue
        path = _package_file(package, safe)
        if path.stat().st_size > MAX_ENTRY_BYTES:
            continue
        seen.add(name)
        files.append((name, path.read_bytes()))
    return files


def _scene_asset_action(asset: dict, scene_id: str) -> str:
    """copy, skip-type, blocked, or unrelated."""
    if not _referenced_by_scene(asset, scene_id):
        return "unrelated"
    ref = asset.get("ref")
    if not isinstance(ref, str):
        return "blocked"
    if asset.get("hostile") or asset.get("external"):
        return "blocked"
    safe, problem = _safe_ref(ref)
    if problem or not safe:
        return "blocked"
    if Path(safe).suffix.lower() not in LOOSE_IMPORT_SUFFIXES:
        return "skip-type"
    if not asset.get("present_in_package"):
        return "blocked"
    return "copy"


def _referenced_by_scene(asset: dict, scene_id: str) -> bool:
    refs = asset.get("referenced_by")
    if not isinstance(refs, list):
        return False
    return any(
        isinstance(item, dict) and item.get("document_type") == "Scene" and item.get("id") == scene_id
        for item in refs
    )


def _asset_lines(inventory: dict, image_ref: str | None, scene_id: str) -> list[dict]:
    rows = []
    for asset in inventory["assets"]:
        ref = asset.get("ref")
        if not isinstance(ref, str):
            continue
        action = _scene_asset_action(asset, scene_id)
        if action == "copy":
            name = Path(ref).name
            also = ""
            if ref == image_ref:
                also = " The same bytes are the UVTT image."
            rows.append(
                _line(
                    APPROXIMATE,
                    "loose-import",
                    (
                        f'asset "{ref}" is written beside the UVTT file as "{name}". '
                        f"{Path(ref).suffix.lower()} is on Arkenforge's documented import list "
                        f"({LOOSE_IMPORT_LIST}).{also}"
                    ),
                    path=ref,
                )
            )
            continue
        if action == "skip-type":
            rows.append(
                _line(
                    UNSUPPORTED,
                    "asset-type-skipped",
                    (
                        f'asset "{ref}" was skipped. This type is not on Arkenforge\'s documented '
                        f"import list ({LOOSE_IMPORT_LIST})."
                    ),
                    path=ref,
                )
            )
            continue
        if action == "blocked" and _referenced_by_scene(asset, scene_id):
            if asset.get("hostile"):
                reason = "The reference leaves the package and was not opened."
            elif asset.get("external"):
                reason = "External URLs are not fetched."
            elif not asset.get("present_in_package"):
                reason = "The file is not in the package."
            else:
                reason = "The reference was not opened."
            skipped = ""
            if Path(ref).suffix.lower() not in LOOSE_IMPORT_SUFFIXES:
                skipped = (
                    f" Skipped. This type is not on Arkenforge's documented import list "
                    f"({LOOSE_IMPORT_LIST})."
                )
            rows.append(
                _line(
                    UNSUPPORTED,
                    "asset",
                    f'asset "{ref}". {reason}{skipped}',
                    path=ref,
                )
            )
            continue
        if asset.get("hostile"):
            grade = UNSUPPORTED
            reason = "The reference leaves the package and was not opened."
        elif asset.get("external"):
            grade = UNSUPPORTED
            reason = "External URLs are not fetched."
        elif not asset.get("present_in_package"):
            grade = UNSUPPORTED
            reason = "The file is not in the package."
        else:
            suffix = Path(ref).suffix.lower()
            if suffix in LOOSE_IMPORT_SUFFIXES:
                grade = MANUAL
                reason = (
                    "This extension is a confirmed loose import "
                    f"({LOOSE_IMPORT_LIST}). "
                    "It is not referenced by this scene, so it is not written beside the UVTT file."
                )
            else:
                grade = UNSUPPORTED
                reason = (
                    f"Skipped. This type is not on Arkenforge's documented import list "
                    f"({LOOSE_IMPORT_LIST})."
                )
        rows.append(
            _line(
                grade,
                "asset",
                f'asset "{ref}". {reason}',
                path=ref,
            )
        )
    return rows


def _pack_lines(inventory: dict) -> list[dict]:
    rows = []
    for pack in inventory["packs"]:
        if pack.get("decoded") and pack.get("document_count"):
            continue
        name = pack.get("name")
        storage = pack.get("storage")
        rows.append(
            _line(
                UNSUPPORTED,
                "pack-not-in-uvtt",
                (
                    f'pack "{name}" storage {storage} was not loaded into the UVTT file. '
                    "YAML is not executed, and no Arkenforge pack format was used."
                ),
                name=name if isinstance(name, str) else None,
                path=pack.get("path") if isinstance(pack.get("path"), str) else None,
            )
        )
    return rows


def _package_file_lines(inventory: dict) -> list[dict]:
    provenance = inventory["provenance"]
    rows = []
    for script in provenance.get("scripts_not_executed") or []:
        path = script.get("path") if isinstance(script.get("path"), str) else None
        rows.append(
            _line(
                UNSUPPORTED,
                "package-script",
                (
                    f'package script "{path}" was not executed. '
                    "No Arkenforge scripting API was found."
                ),
                path=path,
            )
        )
    for style in provenance.get("styles_not_applied") or []:
        path = style.get("path") if isinstance(style.get("path"), str) else None
        rows.append(
            _line(
                UNSUPPORTED,
                "package-style",
                f'package style "{path}" was not applied. UVTT has no stylesheet.',
                path=path,
            )
        )
    for key in provenance.get("manifest_unmapped") or {}:
        rows.append(
            _line(
                UNSUPPORTED,
                "manifest-field",
                f'manifest field "{key}". UVTT has no package manifest.',
                path=key,
            )
        )
    return rows


def _report(scene_id: str, scene_name: object, lines: list[dict]) -> dict:
    name = scene_name if isinstance(scene_name, str) else None
    buckets = {NATIVE: [], APPROXIMATE: [], MANUAL: [], UNSUPPORTED: []}
    for line in lines:
        buckets[line["grade"]].append(line)
    native = buckets[NATIVE]
    approximate = buckets[APPROXIMATE]
    manual = buckets[MANUAL]
    unsupported = buckets[UNSUPPORTED]
    headline = (
        f"Unsupported {len(unsupported)}. Manual {len(manual)}. "
        f"Approximate {len(approximate)}. Native {len(native)}. "
        "The importable file is UVTT JSON: map image, square grid, line of sight, portals, and lights. "
        "Counts include package inventory as well as the selected scene. Unsupported means this slice did not translate a feature, not that Arkenforge cannot support it. The full selected source scene is preserved separately."
    )
    return {
        "headline": headline,
        "scene_id": scene_id,
        "scene_name": name,
        "source": UVTT_SOURCE,
        "read_on": UVTT_READ_ON,
        "page_modified": UVTT_PAGE_MODIFIED,
        "native": native,
        "approximate": approximate,
        "manual": manual,
        "unsupported": unsupported,
        "counts": {
            "native": len(native),
            "approximate": len(approximate),
            "manual": len(manual),
            "unsupported": len(unsupported),
        },
    }


def _image_ref(lines: list[dict]) -> str | None:
    for line in lines:
        if line["code"] == "image":
            return line.get("path")
    return None


def _line(
    grade: str,
    code: str,
    summary: str,
    *,
    document_type: str | None = None,
    id: str | None = None,
    name: str | None = None,
    path: str | None = None,
) -> dict:
    prefix = _GRADE_PREFIX.get(grade)
    if prefix is None:
        raise InventoryFatal(f"unknown UVTT grade {grade}")
    text = summary.strip()
    for old in ("Native:", "Approximate:", "Manual:", "Unsupported:", "Carried:", "Dropped:", "Gap:"):
        if text.startswith(old):
            text = text[len(old):].lstrip()
            break
    return {
        "grade": grade,
        "code": code,
        "summary": f"{prefix} {text}",
        "document_type": document_type,
        "id": id,
        "name": name,
        "path": path,
    }


def _dicts(value: object) -> list[dict]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _texture_src(tile: dict) -> str | None:
    texture = tile.get("texture")
    if isinstance(texture, dict) and isinstance(texture.get("src"), str):
        return texture["src"]
    if isinstance(tile.get("img"), str):
        return tile["img"]
    return None


def _segment(raw: object, size: float) -> tuple[tuple[float, float], tuple[float, float]] | None:
    if not isinstance(raw, list) or len(raw) != 4:
        return None
    numbers = [_number(item) for item in raw]
    if any(item is None for item in numbers):
        return None
    x1, y1, x2, y2 = (item / size for item in numbers)
    return (x1, y1), (x2, y2)


def _text_id(node: dict) -> str | None:
    value = node.get("_id")
    return value if isinstance(value, str) else None


def _text_name(node: dict) -> str | None:
    value = node.get("name")
    return value if isinstance(value, str) else None


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return float(value)


def _coord(value: float) -> int | float:
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _plain(value: float) -> str:
    return str(_coord(value))


def _hex_color(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) not in {4, 7} or not value.startswith("#"):
        return False
    return all(char in "0123456789abcdefABCDEF" for char in value[1:])
