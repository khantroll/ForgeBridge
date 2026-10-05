"""Build fixtures/synthetic-leveldb with plyvel.

The keys match foundryvtt-cli 0.0.6 (retrieved 2026-10-03): UTF-8 keys, JSON
values, primary key `!<collection>!<id>`, embedded key
`!<collection>.<field>!<parentId>.<embeddedId>`.

Requires plyvel-next==2.1.2, the LevelDB binding pinned in requirements.txt.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ENTRIES = [
    (
        "!actors!actor-leveldb",
        {
            "_id": "actor-leveldb",
            "name": "Level Mummy",
            "type": "npc",
            "img": "assets/no-such.webp",
            "effects": ["effect-leveldb"],
            "items": [],
            "homebrewRule": {"dc": 12},
            "notACoreField": {"reason": "leveldb retained"},
        },
    ),
    (
        "!actors.effects!actor-leveldb.effect-leveldb",
        {
            "_id": "effect-leveldb",
            "name": "Dread",
            "disabled": False,
            "changes": [],
        },
    ),
    (
        "!actors!actor-whisper",
        {
            "_id": "actor-whisper",
            "name": "Whisper",
            "type": "npc",
            "effects": [],
            "items": [],
            "system": {
                "note": "require('fs').writeFileSync('/tmp/forgebridge-leveldb-executed','from-leveldb')"
            },
        },
    ),
    (
        "!folders!folder-crypt",
        {
            "_id": "folder-crypt",
            "name": "Crypt Folder",
            "type": "Actor",
            "folder": None,
        },
    ),
]


# Scene pack for fixtures/synthetic-leveldb-scene. Embedded walls, lights, and
# the other placeables use the same !<collection>.<field>!<parent>.<id> keys.
SCENE_ENTRIES = [
    (
        "!scenes!scene-vault",
        {
            "_id": "scene-vault",
            "name": "Level Vault",
            "width": 200,
            "height": 200,
            "img": "assets/crypt.png",
            "grid": {"type": 1, "size": 100, "distance": 5, "units": "ft"},
            "thumb": "assets/crypt.png",
            "levels": ["level-ground"],
            "walls": ["wall-door"],
            "lights": ["light-torch"],
            "sounds": ["sound-drip"],
            "tokens": ["token-vault"],
            "tiles": ["tile-sarcophagus", "tile-hostile"],
            "notes": ["note-vault"],
            "regions": ["region-vault"],
            "flags": {"forgebridge-synthetic": {"kept": True}},
            "notACoreField": {"reason": "leveldb scene retained"},
        },
    ),
    (
        "!scenes.levels!scene-vault.level-ground",
        {
            "_id": "level-ground",
            "name": "Ground",
            "background": {"src": "assets/crypt.png"},
        },
    ),
    (
        "!scenes.walls!scene-vault.wall-door",
        {"_id": "wall-door", "c": [0, 0, 100, 0], "door": 1, "ds": 0},
    ),
    (
        "!scenes.lights!scene-vault.light-torch",
        {
            "_id": "light-torch",
            "x": 50,
            "y": 50,
            "config": {"dim": 20, "bright": 10, "color": "#ffcc88"},
        },
    ),
    (
        "!scenes.sounds!scene-vault.sound-drip",
        {"_id": "sound-drip", "x": 40, "y": 40, "path": "assets/drip.wav", "radius": 10},
    ),
    (
        "!scenes.tokens!scene-vault.token-vault",
        {
            "_id": "token-vault",
            "name": "VaultToken",
            "x": 60,
            "y": 60,
            "texture": {"src": "assets/crypt.png"},
        },
    ),
    (
        "!scenes.tiles!scene-vault.tile-sarcophagus",
        {"_id": "tile-sarcophagus", "texture": {"src": "assets/crypt.png"}},
    ),
    (
        "!scenes.tiles!scene-vault.tile-hostile",
        {"_id": "tile-hostile", "texture": {"src": "../../etc/passwd"}},
    ),
    (
        "!scenes.notes!scene-vault.note-vault",
        {"_id": "note-vault", "text": "Sarcophagus"},
    ),
    (
        "!scenes.regions!scene-vault.region-vault",
        {
            "_id": "region-vault",
            "name": "Vault trigger",
            "behaviors": [
                {
                    "_id": "behavior-open",
                    "name": "Open vault",
                    "type": "executeScript",
                    "system": {
                        "script": "require('fs').writeFileSync('/tmp/forgebridge-region-executed','region')"
                    },
                }
            ],
        },
    ),
    (
        "!actors!actor-vault",
        {
            "_id": "actor-vault",
            "name": "Vault Keeper",
            "type": "npc",
            "effects": [],
            "items": [],
            "img": "assets/no-such.webp",
            "homebrewRule": {"dc": 9},
            "system": {
                "note": "require('fs').writeFileSync('/tmp/forgebridge-leveldb-executed','from-scene')"
            },
        },
    ),
    (
        "!journal!journal-vault",
        {"_id": "journal-vault", "name": "Vault note", "pages": []},
    ),
]


def build(dest: Path) -> None:
    _write(dest, ENTRIES)


def build_scene(dest: Path) -> None:
    _write(dest, SCENE_ENTRIES)


def _write(dest: Path, entries: list) -> None:
    import plyvel

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    database = plyvel.DB(str(dest), create_if_missing=True)
    try:
        for key, document in entries:
            database.put(key.encode("utf-8"), json.dumps(document).encode("utf-8"))
        database.compact_range()
    finally:
        database.close()
    lock = dest / "LOCK"
    if lock.exists():
        lock.unlink()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    build(root / "fixtures" / "synthetic-leveldb" / "packs" / "actors")
    build_scene(root / "fixtures" / "synthetic-leveldb-scene" / "packs" / "scenes")
