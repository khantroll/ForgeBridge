"""LevelDB compendium inventory. NeDB coverage stays in test_inventory.py."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
LEVELDB = REPO / "fixtures" / "synthetic-leveldb"
POINTER = REPO / "fixtures" / "leveldb-pointer"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(REPO / "scripts"))

import build_synthetic_leveldb as leveldb_fixture  # noqa: E402

from forgebridge.inventory import inventory_path  # noqa: E402
from forgebridge.leveldb import read_leveldb_bytes  # noqa: E402
from forgebridge.validate import load_schema, validate  # noqa: E402

MARKER = Path("/tmp/forgebridge-leveldb-executed")


class LevelDBInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        if MARKER.exists():
            MARKER.unlink()

    def tearDown(self) -> None:
        if MARKER.exists():
            MARKER.unlink()

    def test_synthetic_leveldb_pack_is_inventoried(self) -> None:
        document = inventory_path(LEVELDB)
        self.assertEqual(validate(document, load_schema()), [])
        pack = document["packs"][0]
        self.assertEqual(pack["storage"], "leveldb")
        self.assertTrue(pack["decoded"])
        self.assertEqual(pack["document_count"], 3)
        self.assertEqual(document["counts"]["documents_by_type"], {"Actor": 2, "Folder": 1})
        self.assertEqual(document["counts"]["embedded_by_type"], {"ActiveEffect": 1})

        mummy = next(item for item in document["documents"] if item["id"] == "actor-leveldb")
        self.assertEqual(mummy["document_type"], "Actor")
        self.assertEqual(mummy["name"], "Level Mummy")
        self.assertEqual(mummy["embedded_counts"], {"ActiveEffect": 1})
        source = mummy["retained_fields"]["_unpinned_source"]
        self.assertEqual(source["homebrewRule"], {"dc": 12})
        self.assertEqual(source["notACoreField"], {"reason": "leveldb retained"})
        self.assertEqual(source["effects"][0]["name"], "Dread")

        whisper = next(item for item in document["documents"] if item["id"] == "actor-whisper")
        self.assertIn("writeFileSync", json.dumps(whisper["retained_fields"]))
        folder = next(item for item in document["documents"] if item["id"] == "folder-crypt")
        self.assertEqual(folder["document_type"], "Folder")
        self.assertEqual(folder["name"], "Crypt Folder")

        effect = document["behaviors"][0]
        self.assertEqual(effect["name"], "Dread")
        self.assertIs(effect["executed"], False)
        self.assertIs(effect["interpreted"], False)
        missing = next(asset for asset in document["assets"] if asset["ref"] == "assets/no-such.webp")
        self.assertFalse(missing["present_in_package"])
        self.assertFalse(MARKER.exists())

    def test_rebuilt_pack_matches_the_committed_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "synthetic-leveldb"
            (root / "packs").mkdir(parents=True)
            leveldb_fixture.build(root / "packs" / "actors")
            (root / "module.json").write_text((LEVELDB / "module.json").read_text(encoding="utf-8"), encoding="utf-8")
            rebuilt = inventory_path(root)
        committed = inventory_path(LEVELDB)
        self.assertEqual(
            [item["id"] for item in rebuilt["documents"]],
            [item["id"] for item in committed["documents"]],
        )
        self.assertEqual(rebuilt["counts"]["documents_by_type"], committed["counts"]["documents_by_type"])
        self.assertFalse(MARKER.exists())

    def test_zip_of_leveldb_matches_the_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "synthetic-leveldb.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                for path in LEVELDB.rglob("*"):
                    if path.is_file():
                        handle.write(path, Path("synthetic-leveldb") / path.relative_to(LEVELDB))
            zipped = inventory_path(archive)
        self.assertEqual(validate(zipped, load_schema()), [])
        self.assertTrue(zipped["packs"][0]["decoded"])
        self.assertEqual(
            [(item["document_type"], item["id"]) for item in zipped["documents"]],
            [("Actor", "actor-leveldb"), ("Actor", "actor-whisper"), ("Folder", "folder-crypt")],
        )
        self.assertFalse(MARKER.exists())

    def test_pointer_directory_is_not_read_as_text(self) -> None:
        document = inventory_path(POINTER)
        self.assertEqual(validate(document, load_schema()), [])
        pack = document["packs"][0]
        self.assertEqual(pack["storage"], "leveldb")
        self.assertFalse(pack["decoded"])
        self.assertEqual(pack["document_count"], 0)
        self.assertEqual(document["documents"], [])
        self.assertNotIn("should-not-import", json.dumps(document))
        self.assertIn("leveldb-not-decoded", {item["code"] for item in document["diagnostics"]})
        self.assertFalse(MARKER.exists())

    def test_snapshot_rejects_cross_platform_path_escapes_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "must-not-be-written"
            unsafe = ["../escape", "..\\escape", str(outside),
                      "C:\\escape", "C:escape", "CURRENT:stream",
                      "\\\\server\\share\\escape", "bad\x00name", "", ".", ".."]
            seen = []

            def inspect_snapshot(dest, result, **kwargs):
                seen.extend((path.name, path.read_bytes()) for path in dest.iterdir())

            with patch("forgebridge.leveldb._open_and_decode", side_effect=inspect_snapshot):
                result = read_leveldb_bytes(
                    {**dict.fromkeys(unsafe, b"untrusted"), "CURRENT": b"MANIFEST-000001\n"},
                    max_entries=10, max_value_bytes=100,
                )
            self.assertFalse(outside.exists())
        self.assertEqual(seen, [("CURRENT", b"MANIFEST-000001\n")])
        self.assertEqual(len(result.diagnostics), len(unsafe))
        self.assertEqual({code for _, code, _ in result.diagnostics}, {"leveldb-skipped-name"})


if __name__ == "__main__":
    unittest.main()
