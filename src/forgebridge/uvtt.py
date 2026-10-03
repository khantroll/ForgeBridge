"""Write one Foundry scene as UVTT JSON, plus a loss report.

The UVTT object uses only the core fields on
https://arkenforge.com/universal-vtt-files/
read 2026-10-03. That page's dateModified is 2026-08-22.
Core fields used: format, resolution.map_origin, resolution.map_size,
resolution.pixels_per_grid, line_of_sight, objects_line_of_sight, portals
(position, bounds, rotation, closed, freestanding), environment.baked_lighting,
environment.lights (position, color), and image.
software and creator are Arkenforge extras on that page, so they are omitted.
The page does not publish the format decimal and does not show a bounds example.

Foundry constants used for this slice, Version 14 API, retrieved 2026-10-03:
GRID_TYPES.SQUARE is 1. WALL_DOOR_TYPES values that become portals are 1 and 2.
WALL_DOOR_STATES: CLOSED 0, OPEN 1, LOCKED 2.
LightData.bright, LightData.dim, and LightData.shadows are numbers. The light
page does not state a unit for bright or dim. UVTT shadows is a bool, so those
three are left out of the file.
"""

from __future__ import annotations

import base64
import json
import math
from pathlib import Path

from forgebridge.inventory import MAX_ENTRY_BYTES, _safe_ref, inventory_path
from forgebridge.validate import InventoryFatal

UVTT_SOURCE = "https://arkenforge.com/universal-vtt-files/"
UVTT_READ_ON = "2026-10-03"
UVTT_PAGE_MODIFIED = "2026-08-22"

GRID_SQUARE = 1
PORTAL_DOOR_CODES = {1, 2}
DOOR_CLOSED = 0
DOOR_OPEN = 1
DOOR_LOCKED = 2

SCENE_FIELDS_EXPLAINED = {
    "_id",
    "name",
    "width",
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


def build_uvtt_slice(package: Path, scene_id: str) -> dict:
    """Return {"uvtt", "loss_report"} for one scene in a module folder."""
    if not package.is_dir():
        raise InventoryFatal(
            "UVTT slice reads a module folder. Zip archives are not read by this slice."
        )
    if package.is_symlink():
        raise InventoryFatal("UVTT slice does not follow a symlinked package root.")
    inventory = inventory_path(package)
    scene_row = _scene_row(inventory, scene_id)
    payload = _load_scene_payload(package, scene_row, scene_id)
    uvtt, carried, dropped, gaps = _scene_to_uvtt(package, payload)
    dropped.extend(_other_document_drops(inventory, scene_id))
    dropped.extend(_behavior_drops(inventory))
    dropped.extend(_asset_drops(inventory, _carried_image_ref(carried)))
    dropped.extend(_pack_drops(inventory))
    dropped.extend(_package_file_drops(inventory))
    report = _report(scene_id, payload.get("name"), carried, dropped, gaps)
    return {"uvtt": uvtt, "loss_report": report}


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
    if storage not in {"nedb", "json"}:
        raise InventoryFatal(
            f"scene {scene_id!r} is stored as {storage}. This slice does not decode that storage."
        )
    return row


def _load_scene_payload(package: Path, row: dict, scene_id: str) -> dict:
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
    for payload in payloads:
        doc_id = payload.get("_id") if isinstance(payload.get("_id"), str) else None
        if doc_id is None and isinstance(payload.get("id"), str):
            doc_id = payload["id"]
        if doc_id == scene_id:
            return payload
    raise InventoryFatal(f"scene {scene_id!r} was not in {safe}")


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


def _scene_to_uvtt(package: Path, scene: dict) -> tuple[dict, list[dict], list[dict], list[dict]]:
    carried: list[dict] = []
    dropped: list[dict] = []
    gaps: list[dict] = []
    size = _square_grid(scene)
    image_ref, image_bytes = _scene_image(package, scene)
    _drop_scene_fields(scene, image_ref, dropped)
    walls = scene.get("walls") if isinstance(scene.get("walls"), list) else []
    lights = scene.get("lights") if isinstance(scene.get("lights"), list) else []
    line_of_sight, portals = _walls_to_uvtt(walls, size, carried, dropped)
    uvtt_lights = _lights_to_uvtt(lights, size, carried, dropped)
    width = _number(scene.get("width"))
    height = _number(scene.get("height"))
    if width is None or height is None or width <= 0 or height <= 0:
        raise InventoryFatal("scene width and height must be positive numbers")
    carried.append(
        _line(
            "carried",
            "resolution",
            (
                f"Carried: grid { _plain(width) } by { _plain(height) } pixels at "
                f"{ _plain(size) } pixels per square, as map_size "
                f"{ _plain(width / size) } by { _plain(height / size) } and map_origin 0, 0."
            ),
            document_type="Scene",
            id=scene.get("_id") if isinstance(scene.get("_id"), str) else None,
            name=scene.get("name") if isinstance(scene.get("name"), str) else None,
            path=image_ref,
        )
    )
    carried.append(
        _line(
            "carried",
            "image",
            (
                f"Carried: image {image_ref} from the level background, once, as base64. "
                "Scene img was not written again when it pointed at the same file."
            ),
            document_type="Scene",
            id=_text_id(scene),
            name=_text_name(scene),
            path=image_ref,
        )
    )
    carried.append(
        _line(
            "carried",
            "baked-lighting",
            "Carried: environment.baked_lighting false. The scene lights are separate data, not paint in the image.",
            document_type="Scene",
            id=_text_id(scene),
            name=_text_name(scene),
            path=image_ref,
        )
    )
    gaps.append(
        _line(
            "gap",
            "format-decimal-unpublished",
            (
                "Gap: format is documented as a decimal version. The UVTT page, read "
                f"{UVTT_READ_ON}, does not publish that number. This slice writes 0.0 "
                "as a placeholder and does not claim that Arkenforge expects 0.0."
            ),
            path=UVTT_SOURCE,
        )
    )
    gaps.append(
        _line(
            "gap",
            "portal-bounds-unspecified",
            (
                "Gap: portal bounds are documented as an array of x,y values. The UVTT page, read "
                f"{UVTT_READ_ON}, has no example. This slice writes [x, y] pairs relative to position."
            ),
            path=UVTT_SOURCE,
        )
    )
    gaps.append(
        _line(
            "gap",
            "freestanding-undefined",
            (
                "Gap: freestanding is a documented bool. The UVTT page, read "
                f"{UVTT_READ_ON}, does not define it. This slice sets it false because the portal is a wall segment."
            ),
            path=UVTT_SOURCE,
        )
    )
    gaps.append(
        _line(
            "gap",
            "software-creator-not-core",
            (
                "Gap: the UVTT page says Arkenforge writes software and creator as its own extra tags. "
                "They are outside the core list, so this slice omits both."
            ),
            path=UVTT_SOURCE,
        )
    )
    uvtt = {
        "format": 0.0,
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
            "lights": uvtt_lights,
        },
        "image": base64.b64encode(image_bytes).decode("ascii"),
    }
    return uvtt, carried, dropped, gaps


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
    return safe, data


def _package_file(package: Path, safe: str) -> Path:
    root = package.resolve()
    path = package / safe
    current = path
    while True:
        if current.is_symlink():
            raise InventoryFatal(f"symlink was not followed: {safe}")
        if current.resolve() == root or current == package:
            break
        parent = current.parent
        if parent == current:
            break
        current = parent
    if not _contained(root, path) or not path.is_file():
        raise InventoryFatal(f"path is not a file inside the package: {safe}")
    return path


def _contained(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except (OSError, ValueError):
        return False
    return True


def _drop_scene_fields(scene: dict, image_ref: str, dropped: list[dict]) -> None:
    scene_id = _text_id(scene)
    scene_name = _text_name(scene)
    if scene_name:
        dropped.append(
            _line(
                "dropped",
                "scene-name",
                f'Dropped: scene name "{scene_name}". The UVTT core fields have no name.',
                document_type="Scene",
                id=scene_id,
                name=scene_name,
            )
        )
    grid = scene.get("grid") if isinstance(scene.get("grid"), dict) else {}
    if "distance" in grid or "units" in grid:
        distance = grid.get("distance")
        units = grid.get("units")
        dropped.append(
            _line(
                "dropped",
                "grid-distance",
                (
                    f"Dropped: grid distance {distance} units {units!r}. "
                    "UVTT resolution has map_origin, map_size, and pixels_per_grid only."
                ),
                document_type="Scene",
                id=scene_id,
                name=scene_name,
                path="grid",
            )
        )
    thumb = scene.get("thumb")
    if isinstance(thumb, str) and thumb.strip():
        dropped.append(
            _line(
                "dropped",
                "scene-thumb",
                (
                    f'Dropped: scene thumb "{thumb}". UVTT is one image, taken from the level background, '
                    "so the thumbnail was left out."
                ),
                document_type="Scene",
                id=scene_id,
                name=scene_name,
                path=thumb,
            )
        )
    img = scene.get("img")
    if isinstance(img, str) and img.strip() and img != image_ref:
        dropped.append(
            _line(
                "dropped",
                "scene-img-not-chosen",
                f'Dropped: scene img "{img}". The UVTT image is the level background "{image_ref}".',
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
        dropped.append(
            _line(
                "dropped",
                "level-not-image",
                (
                    f"Dropped: level {label}{ident}. Only the background image can become the UVTT image. "
                    "The level name and its other fields were left out."
                ),
                document_type="Level",
                id=level_id,
                name=level_name,
            )
        )
    _drop_placeables(scene, dropped)
    flags = scene.get("flags")
    if isinstance(flags, dict):
        for scope in flags:
            dropped.append(
                _line(
                    "dropped",
                    "scene-flags",
                    f'Dropped: scene flags "{scope}". UVTT has no flags field.',
                    document_type="Scene",
                    id=scene_id,
                    name=scene_name,
                    path=f"flags.{scope}",
                )
            )
    for key in scene:
        if key in SCENE_FIELDS_EXPLAINED:
            continue
        dropped.append(
            _line(
                "dropped",
                "scene-field",
                f'Dropped: scene field "{key}". UVTT has no field by this name, and the value was not copied.',
                document_type="Scene",
                id=scene_id,
                name=scene_name,
                path=key,
            )
        )


def _drop_placeables(scene: dict, dropped: list[dict]) -> None:
    for token in _dicts(scene.get("tokens")):
        name = _text_name(token)
        label = f'"{name}"' if name else "token"
        dropped.append(
            _line(
                "dropped",
                "token",
                (
                    f"Dropped: token {label} ({_text_id(token) or 'no id'}). "
                    "The UVTT page says the file cannot contain individually selectable tokens. "
                    "It was not written to objects_line_of_sight."
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
            path_note = "The path was not opened."
        else:
            path_note = "The file stays in the package and was not written as a second image."
        dropped.append(
            _line(
                "dropped",
                "tile",
                (
                    f'Dropped: tile "{_text_id(tile) or "no id"}" texture "{src}". '
                    f"{path_note} "
                    "UVTT cannot carry a separate map image, so the tile was not written to objects_line_of_sight."
                ),
                document_type="Tile",
                id=_text_id(tile),
                path=src,
            )
        )
    for sound in _dicts(scene.get("sounds")):
        path = sound.get("path") if isinstance(sound.get("path"), str) else None
        dropped.append(
            _line(
                "dropped",
                "ambient-sound",
                (
                    f'Dropped: ambient sound "{_text_id(sound) or "no id"}" path "{path}". '
                    "UVTT has no audio field."
                ),
                document_type="AmbientSound",
                id=_text_id(sound),
                path=path,
            )
        )
    for note in _dicts(scene.get("notes")):
        dropped.append(
            _line(
                "dropped",
                "note",
                f'Dropped: note "{_text_id(note) or "no id"}". UVTT has no notes field, and the note text was not copied.',
                document_type="Note",
                id=_text_id(note),
                name=_text_name(note),
            )
        )
    for region in _dicts(scene.get("regions")):
        name = _text_name(region)
        label = f'"{name}"' if name else "region"
        dropped.append(
            _line(
                "dropped",
                "region",
                (
                    f"Dropped: region {label} ({_text_id(region) or 'no id'}). "
                    "UVTT has no region field, and its behaviors were not executed."
                ),
                document_type="Region",
                id=_text_id(region),
                name=name,
            )
        )


def _walls_to_uvtt(
    walls: list,
    size: float,
    carried: list[dict],
    dropped: list[dict],
) -> tuple[list, list]:
    line_of_sight = []
    portals = []
    for wall in walls:
        if not isinstance(wall, dict):
            continue
        segment = _segment(wall.get("c"), size)
        wall_id = _text_id(wall)
        if segment is None:
            dropped.append(
                _line(
                    "dropped",
                    "wall-geometry",
                    f'Dropped: wall "{wall_id or "no id"}" has no 4-number coordinate list, so no UVTT segment was written.',
                    document_type="Wall",
                    id=wall_id,
                    path="c",
                )
            )
            continue
        (x1, y1), (x2, y2) = segment
        door = wall.get("door")
        if isinstance(door, int) and not isinstance(door, bool) and door in PORTAL_DOOR_CODES:
            closed, state_drop = _portal_closed(wall.get("ds"), wall_id)
            if state_drop is not None:
                dropped.append(state_drop)
            dropped.append(
                _line(
                    "dropped",
                    "door-type",
                    (
                        f'Dropped: wall "{wall_id or "no id"}" door code {door}. '
                        "UVTT portals have no door-type field. The segment was written as a portal."
                    ),
                    document_type="Wall",
                    id=wall_id,
                    path="door",
                )
            )
            mx = _coord((x1 + x2) / 2)
            my = _coord((y1 + y2) / 2)
            portals.append(
                {
                    "position": {"x": mx, "y": my},
                    "bounds": [
                        [_coord(x1 - mx), _coord(y1 - my)],
                        [_coord(x2 - mx), _coord(y2 - my)],
                    ],
                    "rotation": _coord(math.atan2(y2 - y1, x2 - x1)),
                    "closed": closed,
                    "freestanding": False,
                }
            )
            carried.append(
                _line(
                    "carried",
                    "portal",
                    (
                        f'Carried: wall "{wall_id or "no id"}" as a portal. '
                        f"closed is {str(closed).lower()} from door state {wall.get('ds')} "
                        "(CLOSED is 0, OPEN is 1). A locked state is not a separate UVTT value."
                    ),
                    document_type="Wall",
                    id=wall_id,
                    path="c",
                )
            )
            continue
        line_of_sight.append([[_coord(x1), _coord(y1)], [_coord(x2), _coord(y2)]])
        carried.append(
            _line(
                "carried",
                "line-of-sight",
                f'Carried: wall "{wall_id or "no id"}" as one line_of_sight segment. Door code {door!r} is not a portal.',
                document_type="Wall",
                id=wall_id,
                path="c",
            )
        )
    if not line_of_sight:
        carried.append(
            _line(
                "carried",
                "line-of-sight-empty",
                "Carried: line_of_sight is empty. Door walls were written as portals and were not also written as walls.",
                document_type="Wall",
            )
        )
    return line_of_sight, portals


def _portal_closed(ds: object, wall_id: str | None) -> tuple[bool, dict | None]:
    if ds == DOOR_OPEN:
        return False, None
    if ds == DOOR_LOCKED:
        return True, _line(
            "dropped",
            "door-locked",
            (
                f'Dropped: wall "{wall_id or "no id"}" door state LOCKED (2). '
                "UVTT closed is only a bool, so the portal is closed and the locked state was left out."
            ),
            document_type="Wall",
            id=wall_id,
            path="ds",
        )
    if ds == DOOR_CLOSED:
        return True, None
    return True, _line(
        "dropped",
        "door-state",
        (
            f'Dropped: wall "{wall_id or "no id"}" door state {ds!r} is outside CLOSED 0, OPEN 1, and LOCKED 2. '
            "The portal was written closed."
        ),
        document_type="Wall",
        id=wall_id,
        path="ds",
    )


def _lights_to_uvtt(lights: list, size: float, carried: list[dict], dropped: list[dict]) -> list[dict]:
    written = []
    for light in lights:
        if not isinstance(light, dict):
            continue
        light_id = _text_id(light)
        config = light.get("config") if isinstance(light.get("config"), dict) else {}
        color = config.get("color") if isinstance(config.get("color"), str) else None
        x = _number(light.get("x"))
        y = _number(light.get("y"))
        dim = config.get("dim")
        bright = config.get("bright")
        dropped.append(
            _line(
                "dropped",
                "light-range",
                (
                    f'Dropped: light "{light_id or "no id"}" dim {dim!r} and bright {bright!r} '
                    "were not written as range or intensity. Foundry LightData records dim, bright, "
                    "and shadows as numbers and does not state the unit. UVTT shadows is a bool. "
                    "No range, intensity, or shadows value was written."
                ),
                document_type="AmbientLight",
                id=light_id,
                path="config",
            )
        )
        if x is None or y is None or not _hex_color(color):
            dropped.append(
                _line(
                    "dropped",
                    "light-not-written",
                    f'Dropped: light "{light_id or "no id"}" has no square position and hex color, so no UVTT light was written.',
                    document_type="AmbientLight",
                    id=light_id,
                )
            )
            continue
        written.append(
            {
                "position": {"x": _coord(x / size), "y": _coord(y / size)},
                "color": color,
            }
        )
        carried.append(
            _line(
                "carried",
                "light",
                f'Carried: light "{light_id or "no id"}" position and color {color} only.',
                document_type="AmbientLight",
                id=light_id,
                path="config.color",
            )
        )
    return written


def _other_document_drops(inventory: dict, scene_id: str) -> list[dict]:
    rows = []
    for doc in inventory["documents"]:
        if doc.get("document_type") == "Scene" and doc.get("id") == scene_id:
            continue
        dtype = doc.get("document_type") or "Unknown"
        name = doc.get("name") if isinstance(doc.get("name"), str) else None
        doc_id = doc.get("id") if isinstance(doc.get("id"), str) else None
        label = f'"{name}"' if name else "(unnamed)"
        ident = f" ({doc_id})" if doc_id else ""
        tail = " UVTT has no field for this document."
        if dtype == "JournalEntry":
            tail += " Its page text was not interpreted."
        if dtype == "Macro":
            tail += " It was not executed."
        rows.append(
            _line(
                "dropped",
                "document-not-in-uvtt",
                f"Dropped: {dtype} {label}{ident}.{tail}",
                document_type=dtype,
                id=doc_id,
                name=name,
                path=doc.get("source_path") if isinstance(doc.get("source_path"), str) else None,
            )
        )
        rows.extend(_retained_field_drops(doc))
    return rows


def _retained_field_drops(doc: dict) -> list[dict]:
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
                "dropped",
                "retained-field",
                (
                    f'Dropped: field "{key}" on {doc.get("document_type")} '
                    f'"{doc.get("name")}" ({doc.get("id")}). The value was not copied.'
                ),
                document_type=doc.get("document_type") if isinstance(doc.get("document_type"), str) else None,
                id=doc.get("id") if isinstance(doc.get("id"), str) else None,
                name=doc.get("name") if isinstance(doc.get("name"), str) else None,
                path=key,
            )
        )
    return rows


def _behavior_drops(inventory: dict) -> list[dict]:
    rows = []
    for behavior in inventory["behaviors"]:
        kind = behavior.get("kind") if isinstance(behavior.get("kind"), str) else "behavior"
        name = behavior.get("name") if isinstance(behavior.get("name"), str) else None
        label = f'"{name}"' if name else kind
        rows.append(
            _line(
                "dropped",
                "behavior-not-executed",
                f"Dropped: {kind} {label} was not executed and has no UVTT field.",
                document_type=kind,
                id=behavior.get("id") if isinstance(behavior.get("id"), str) else None,
                name=name,
                path=behavior.get("source_path") if isinstance(behavior.get("source_path"), str) else None,
            )
        )
    return rows


def _asset_drops(inventory: dict, carried_ref: str | None) -> list[dict]:
    rows = []
    for asset in inventory["assets"]:
        ref = asset.get("ref")
        if not isinstance(ref, str):
            continue
        if ref == carried_ref and asset.get("present_in_package") and not asset.get("hostile") and not asset.get("external"):
            continue
        if asset.get("hostile"):
            reason = "The reference leaves the package and was not opened."
        elif asset.get("external"):
            reason = "External URLs are not fetched."
        elif not asset.get("present_in_package"):
            reason = "The file is not in the package."
        elif not asset.get("referenced_by"):
            reason = "It is in the package and referenced by no document."
        else:
            reason = "UVTT has no field for this file."
        rows.append(
            _line(
                "dropped",
                "asset",
                f'Dropped: asset "{ref}". {reason}',
                path=ref,
            )
        )
    return rows


def _pack_drops(inventory: dict) -> list[dict]:
    rows = []
    for pack in inventory["packs"]:
        if pack.get("decoded") and pack.get("document_count"):
            continue
        name = pack.get("name")
        storage = pack.get("storage")
        rows.append(
            _line(
                "dropped",
                "pack-not-in-uvtt",
                f'Dropped: pack "{name}" storage {storage} was not written to UVTT.',
                name=name if isinstance(name, str) else None,
                path=pack.get("path") if isinstance(pack.get("path"), str) else None,
            )
        )
    return rows


def _package_file_drops(inventory: dict) -> list[dict]:
    provenance = inventory["provenance"]
    rows = []
    for script in provenance.get("scripts_not_executed") or []:
        path = script.get("path") if isinstance(script.get("path"), str) else None
        rows.append(
            _line(
                "dropped",
                "package-script",
                f'Dropped: package script "{path}" was not executed.',
                path=path,
            )
        )
    for style in provenance.get("styles_not_applied") or []:
        path = style.get("path") if isinstance(style.get("path"), str) else None
        rows.append(
            _line(
                "dropped",
                "package-style",
                f'Dropped: package style "{path}" was not applied.',
                path=path,
            )
        )
    for key in provenance.get("manifest_unmapped") or {}:
        rows.append(
            _line(
                "dropped",
                "manifest-field",
                f'Dropped: manifest field "{key}". UVTT has no package manifest.',
                path=key,
            )
        )
    return rows


def _report(scene_id: str, scene_name: object, carried: list[dict], dropped: list[dict], gaps: list[dict]) -> dict:
    name = scene_name if isinstance(scene_name, str) else None
    headline = (
        f"Dropped {len(dropped)}. Carried {len(carried)}. Gaps {len(gaps)}. "
        "The UVTT file is one map image with walls, portals, and lights. "
        "Everything else in this inventory was left out."
    )
    return {
        "headline": headline,
        "scene_id": scene_id,
        "scene_name": name,
        "source": UVTT_SOURCE,
        "read_on": UVTT_READ_ON,
        "page_modified": UVTT_PAGE_MODIFIED,
        "carried": carried,
        "dropped": dropped,
        "gaps": gaps,
    }


def _carried_image_ref(carried: list[dict]) -> str | None:
    for line in carried:
        if line["code"] == "image":
            return line.get("path")
    return None


def _line(
    severity: str,
    code: str,
    summary: str,
    *,
    document_type: str | None = None,
    id: str | None = None,
    name: str | None = None,
    path: str | None = None,
) -> dict:
    return {
        "severity": severity,
        "code": code,
        "summary": summary,
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
