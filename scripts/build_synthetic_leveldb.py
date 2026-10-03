"""Build fixtures/synthetic-leveldb with plyvel.

The keys match foundryvtt-cli 0.0.6 (retrieved 2026-10-03): UTF-8 keys, JSON
values, primary key `!<collection>!<id>`, embedded key
`!<collection>.<field>!<parentId>.<embeddedId>`.

Requires plyvel==1.5.1, the LevelDB binding pinned in requirements.txt.
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


def build(dest: Path) -> None:
    import plyvel

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    database = plyvel.DB(str(dest), create_if_missing=True)
    try:
        for key, document in ENTRIES:
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
