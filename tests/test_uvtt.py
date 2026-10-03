"""UVTT slice: one synthetic scene, plus a loss report, produced by code."""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
FIXTURE = REPO / "fixtures" / "synthetic-module"
sys.path.insert(0, str(SRC))

from forgebridge.uvtt import build_uvtt_slice  # noqa: E402
from forgebridge.validate import InventoryFatal, load_schema, repo_schema, validate  # noqa: E402

MARKERS = [
    "/tmp/forgebridge-script-executed",
    "/tmp/forgebridge-macro-executed",
    "/tmp/forgebridge-region-executed",
    "/tmp/forgebridge-html-executed",
    "/tmp/forgebridge-yaml-executed",
    "/tmp/forgebridge-leveldb-executed",
    "/tmp/forgebridge-zip-executed",
    "/tmp/forgebridge-abs.js",
]

PHRASES = [
    "Mummy",
    "Stone",
    "Tomb note",
    "Synthetic Loot",
    "Drips",
    "Open tomb",
    "Announce",
    "Despair",
    "Mummy01",
    "drip.wav",
    "orphan",
    "../../etc/passwd",
    "no-such",
    "example.invalid",
    "not executed",
    "notACoreField",
    "homebrewRule",
    "region",
    "tile",
]


def _clear_markers() -> None:
    for marker in MARKERS:
        path = Path(marker)
        if path.exists():
            path.unlink()


def _slice() -> dict:
    return build_uvtt_slice(FIXTURE, "scene-crypt")


class UvttSliceTests(unittest.TestCase):
    def setUp(self) -> None:
        _clear_markers()

    def tearDown(self) -> None:
        _clear_markers()

    def test_scene_crypt_matches_core_schema_and_bytes(self) -> None:
        document = _slice()
        uvtt = document["uvtt"]
        report = document["loss_report"]
        self.assertEqual(validate(uvtt, load_schema(repo_schema("uvtt-core.schema.json"))), [])
        self.assertEqual(validate(report, load_schema(repo_schema("uvtt-loss-report.schema.json"))), [])
        self.assertEqual(
            set(uvtt),
            {
                "format",
                "resolution",
                "line_of_sight",
                "objects_line_of_sight",
                "portals",
                "environment",
                "image",
            },
        )
        self.assertNotIn("software", uvtt)
        self.assertNotIn("creator", uvtt)
        self.assertEqual(uvtt["format"], 0.0)
        self.assertEqual(uvtt["resolution"]["map_origin"], {"x": 0, "y": 0})
        self.assertEqual(uvtt["resolution"]["map_size"], {"x": 2, "y": 2})
        self.assertEqual(uvtt["resolution"]["pixels_per_grid"], 100)
        self.assertEqual(uvtt["line_of_sight"], [])
        self.assertEqual(uvtt["objects_line_of_sight"], [])
        portal = uvtt["portals"][0]
        self.assertEqual(portal["position"], {"x": 0.5, "y": 0})
        self.assertEqual(portal["bounds"], [[-0.5, 0], [0.5, 0]])
        self.assertEqual(portal["rotation"], 0)
        self.assertIs(portal["closed"], True)
        self.assertIs(portal["freestanding"], False)
        self.assertNotIn("ambient_light", uvtt["environment"])
        self.assertIs(uvtt["environment"]["baked_lighting"], False)
        light = uvtt["environment"]["lights"][0]
        self.assertEqual(light["position"], {"x": 0.5, "y": 0.5})
        self.assertEqual(light["color"], "#ffcc88")
        self.assertNotIn("range", light)
        self.assertNotIn("intensity", light)
        self.assertNotIn("shadows", light)
        raw = (FIXTURE / "assets" / "crypt.png").read_bytes()
        self.assertEqual(base64.b64decode(uvtt["image"]), raw)
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_loss_report_leads_with_dropped_and_names_the_inventory(self) -> None:
        document = _slice()
        report = document["loss_report"]
        self.assertTrue(report["headline"].startswith("Dropped "))
        self.assertGreater(len(report["dropped"]), len(report["carried"]))
        self.assertEqual(report["read_on"], "2026-10-03")
        self.assertEqual(report["page_modified"], "2026-08-22")
        self.assertEqual(report["source"], "https://arkenforge.com/universal-vtt-files/")
        dropped_text = "\n".join(item["summary"] for item in report["dropped"])
        for phrase in PHRASES:
            self.assertIn(phrase, dropped_text, phrase)
        self.assertTrue(all(item["summary"].startswith("Dropped:") for item in report["dropped"]))
        self.assertTrue(all(item["summary"].startswith("Gap:") for item in report["gaps"]))
        gap_text = "\n".join(item["summary"] for item in report["gaps"])
        self.assertIn("does not publish", gap_text)
        self.assertIn("0.0", gap_text)
        self.assertIn("bounds", gap_text)
        blob = json.dumps(document)
        self.assertNotIn("writeFileSync", blob)
        self.assertNotIn("/tmp/forgebridge", blob)
        uvtt_blob = json.dumps(document["uvtt"])
        self.assertNotIn("Mummy01", uvtt_blob)
        self.assertNotIn("homebrewRule", uvtt_blob)
        self.assertNotIn("notACoreField", uvtt_blob)
        self.assertEqual(list(REPO.glob("**/*.uvtt")), [])

    def test_extra_uvtt_key_fails_schema(self) -> None:
        uvtt = _slice()["uvtt"]
        uvtt["software"] = "forgebridge"
        errors = validate(uvtt, load_schema(repo_schema("uvtt-core.schema.json")))
        self.assertTrue(errors)

    def test_non_square_grid_does_not_emit_square_geometry(self) -> None:
        png = (FIXTURE / "assets" / "crypt.png").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "hex-module"
            _write_module(
                root,
                {
                    "_id": "scene-hex",
                    "name": "Hex",
                    "width": 200,
                    "height": 200,
                    "grid": {"type": 2, "size": 100},
                    "levels": [{"background": {"src": "assets/crypt.png"}}],
                    "walls": [{"_id": "wall-solid", "c": [0, 0, 100, 0], "door": 0}],
                },
                png,
            )
            with self.assertRaises(InventoryFatal) as caught:
                build_uvtt_slice(root, "scene-hex")
        self.assertIn("SQUARE", str(caught.exception))
        self.assertIn("does not write", str(caught.exception))

    def test_plain_wall_is_line_of_sight_and_door_is_only_a_portal(self) -> None:
        png = (FIXTURE / "assets" / "crypt.png").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wall-module"
            _write_module(
                root,
                {
                    "_id": "scene-walls",
                    "name": "Walls",
                    "width": 100,
                    "height": 100,
                    "grid": {"type": 1, "size": 100, "distance": 5, "units": "ft"},
                    "levels": [{"background": {"src": "assets/crypt.png"}}],
                    "walls": [
                        {"_id": "wall-solid", "c": [0, 0, 0, 100], "door": 0},
                        {"_id": "wall-door", "c": [0, 0, 100, 0], "door": 1, "ds": 0},
                    ],
                },
                png,
            )
            uvtt = build_uvtt_slice(root, "scene-walls")["uvtt"]
        self.assertEqual(uvtt["line_of_sight"], [[[0, 0], [0, 1]]])
        self.assertEqual(len(uvtt["portals"]), 1)
        self.assertEqual(uvtt["portals"][0]["position"], {"x": 0.5, "y": 0})

    def test_cli_prints_schema_valid_slice(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        completed = subprocess.run(
            [sys.executable, "-m", "forgebridge", str(FIXTURE), "--uvtt-scene", "scene-crypt"],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        document = json.loads(completed.stdout)
        self.assertEqual(validate(document["uvtt"], load_schema(repo_schema("uvtt-core.schema.json"))), [])
        self.assertEqual(validate(document["loss_report"], load_schema(repo_schema("uvtt-loss-report.schema.json"))), [])
        self.assertTrue(document["loss_report"]["headline"].startswith("Dropped "))
        self.assertGreater(
            len(document["loss_report"]["dropped"]),
            len(document["loss_report"]["carried"]),
        )
        missing = subprocess.run(
            [sys.executable, "-m", "forgebridge", str(FIXTURE), "--uvtt-scene", "missing-scene"],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(missing.returncode, 1)
        self.assertEqual(missing.stdout, "")
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_zip_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "module.zip"
            archive.write_bytes(b"not a package")
            with self.assertRaises(InventoryFatal) as caught:
                build_uvtt_slice(archive, "scene-crypt")
        self.assertIn("folder", str(caught.exception))


def _write_module(root: Path, scene: dict, png: bytes) -> None:
    (root / "packs").mkdir(parents=True)
    (root / "assets").mkdir()
    (root / "module.json").write_text(
        json.dumps(
            {
                "id": root.name,
                "title": root.name,
                "version": "0.0.1",
                "packs": [
                    {"name": "scenes", "label": "Scenes", "path": "packs/scenes.db", "type": "Scene"}
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "packs" / "scenes.db").write_text(json.dumps(scene) + "\n", encoding="utf-8")
    (root / "assets" / "crypt.png").write_bytes(png)


if __name__ == "__main__":
    unittest.main()
