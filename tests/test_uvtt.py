"""UVTT slice: one synthetic scene, plus a loss report, produced by code."""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
FIXTURE = REPO / "fixtures" / "synthetic-module"
LEVELDB_SCENE = REPO / "fixtures" / "synthetic-leveldb-scene"
LEVELDB_SCENE_ZIP = REPO / "fixtures" / "synthetic-leveldb-scene.zip"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(REPO / "scripts"))

import build_synthetic_leveldb as leveldb_fixture  # noqa: E402

from forgebridge.inventory import inventory_path  # noqa: E402
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
        self.assertEqual(light["range"], 4)
        self.assertNotIn("intensity", light)
        self.assertNotIn("shadows", light)
        raw = (FIXTURE / "assets" / "crypt.png").read_bytes()
        self.assertEqual(base64.b64decode(uvtt["image"]), raw)
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_loss_report_leads_with_unsupported_and_names_the_inventory(self) -> None:
        document = _slice()
        report = document["loss_report"]
        self.assertTrue(report["headline"].startswith("Unsupported "))
        counts = report["counts"]
        self.assertEqual(counts["native"], len(report["native"]))
        self.assertEqual(counts["approximate"], len(report["approximate"]))
        self.assertEqual(counts["manual"], len(report["manual"]))
        self.assertEqual(counts["unsupported"], len(report["unsupported"]))
        self.assertGreater(counts["unsupported"] + counts["manual"], counts["native"])
        self.assertGreater(counts["manual"], 0)
        self.assertGreater(counts["unsupported"], 0)
        self.assertEqual(report["read_on"], "2026-10-03")
        self.assertEqual(report["page_modified"], "2026-08-22")
        self.assertEqual(report["source"], "https://arkenforge.com/universal-vtt-files/")
        prefixes = {
            "native": "Native:",
            "approximate": "Approximate:",
            "manual": "Manual:",
            "unsupported": "Unsupported:",
        }
        for grade, prefix in prefixes.items():
            self.assertTrue(report[grade], grade)
            self.assertTrue(all(item["grade"] == grade for item in report[grade]))
            self.assertTrue(all(item["summary"].startswith(prefix) for item in report[grade]))
        loss_text = "\n".join(
            item["summary"]
            for grade in ("approximate", "manual", "unsupported")
            for item in report[grade]
        )
        for phrase in PHRASES:
            self.assertIn(phrase, loss_text, phrase)
        approximate_text = "\n".join(item["summary"] for item in report["approximate"])
        self.assertIn("does not publish", approximate_text)
        self.assertIn("0.0", approximate_text)
        self.assertIn("bounds", approximate_text)
        native_codes = {item["code"] for item in report["native"]}
        self.assertIn("image", native_codes)
        self.assertIn("portal", native_codes)
        self.assertIn("light", native_codes)
        self.assertIn("resolution", native_codes)
        manual_types = {item["document_type"] for item in report["manual"]}
        for dtype in ("Actor", "Item", "JournalEntry", "RollTable", "Playlist", "Macro", "Token", "Note"):
            self.assertIn(dtype, manual_types, dtype)
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

    def test_dynamic_lighting_writes_ambient_color_and_range_in_squares(self) -> None:
        png = (FIXTURE / "assets" / "crypt.png").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "lighting-module"
            _write_module(
                root,
                {
                    "_id": "scene-lighting",
                    "name": "Lighting",
                    "width": 400,
                    "height": 400,
                    "grid": {"type": 1, "size": 100, "distance": 5, "units": "ft"},
                    "environment": {"ambient_light": "#223344"},
                    "levels": [{"background": {"src": "assets/crypt.png"}}],
                    "lights": [
                        {"_id": "torch", "x": 150, "y": 250,
                         "config": {"dim": 20, "bright": 10, "color": "#ffaa44",
                                    "luminosity": 0.5, "shadows": 0.2}}
                    ],
                },
                png,
            )
            document = build_uvtt_slice(root, "scene-lighting")
        uvtt = document["uvtt"]
        self.assertEqual(uvtt["environment"]["ambient_light"], "#223344")
        self.assertEqual(
            uvtt["environment"]["lights"][0],
            {"position": {"x": 1.5, "y": 2.5}, "range": 4, "color": "#ffaa44"},
        )
        self.assertEqual(validate(uvtt, load_schema(repo_schema("uvtt-core.schema.json"))), [])
        native_codes = {item["code"] for item in document["loss_report"]["native"]}
        approximate_codes = {item["code"] for item in document["loss_report"]["approximate"]}
        self.assertIn("ambient-light", native_codes)
        self.assertIn("light-range", native_codes)
        self.assertIn("light-bright-radius", approximate_codes)
        self.assertIn("light-rendering-properties", approximate_codes)

    def test_darkness_source_is_reported_without_inventing_uvtt_range(self) -> None:
        png = (FIXTURE / "assets" / "crypt.png").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "darkness-module"
            _write_module(
                root,
                {
                    "_id": "scene-darkness",
                    "name": "Darkness",
                    "width": 200,
                    "height": 200,
                    "grid": {"type": 1, "size": 100, "distance": 5, "units": "ft"},
                    "levels": [{"background": {"src": "assets/crypt.png"}}],
                    "lights": [
                        {"_id": "dark", "x": 100, "y": 100,
                         "config": {"dim": -20, "bright": -10, "color": "#000000"}}
                    ],
                },
                png,
            )
            document = build_uvtt_slice(root, "scene-darkness")
        light = document["uvtt"]["environment"]["lights"][0]
        self.assertNotIn("range", light)
        unsupported_codes = {item["code"] for item in document["loss_report"]["unsupported"]}
        self.assertIn("darkness-source", unsupported_codes)

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
        self.assertTrue(document["loss_report"]["headline"].startswith("Unsupported "))
        self.assertGreater(
            document["loss_report"]["counts"]["unsupported"] + document["loss_report"]["counts"]["manual"],
            document["loss_report"]["counts"]["native"],
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

    def test_uvtt_out_writes_only_the_importable_object(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        raw = (FIXTURE / "assets" / "crypt.png").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out" / "scene-crypt.uvtt"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "forgebridge",
                    str(FIXTURE),
                    "--uvtt-scene",
                    "scene-crypt",
                    "--uvtt-out",
                    str(dest),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            envelope = json.loads(completed.stdout)
            self.assertIn("loss_report", envelope)
            self.assertTrue(envelope["loss_report"]["headline"].startswith("Unsupported "))
            written = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(written, envelope["uvtt"])
            self.assertEqual(validate(written, load_schema(repo_schema("uvtt-core.schema.json"))), [])
            self.assertNotIn("loss_report", written)
            self.assertNotIn("software", written)
            self.assertNotIn("creator", written)
            self.assertEqual(base64.b64decode(written["image"]), raw)
        self.assertEqual(list(REPO.glob("**/*.uvtt")), [])
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_leveldb_scene_writes_importable_uvtt_and_grades(self) -> None:
        inventory = inventory_path(LEVELDB_SCENE)
        scene = next(item for item in inventory["documents"] if item["id"] == "scene-vault")
        self.assertEqual(scene["storage"], "leveldb")
        self.assertEqual(scene["document_type"], "Scene")
        document = build_uvtt_slice(LEVELDB_SCENE, "scene-vault")
        uvtt = document["uvtt"]
        report = document["loss_report"]
        self.assertEqual(validate(uvtt, load_schema(repo_schema("uvtt-core.schema.json"))), [])
        self.assertEqual(validate(report, load_schema(repo_schema("uvtt-loss-report.schema.json"))), [])
        self.assertEqual(uvtt["resolution"]["map_size"], {"x": 2, "y": 2})
        self.assertEqual(uvtt["line_of_sight"], [])
        self.assertEqual(uvtt["portals"][0]["position"], {"x": 0.5, "y": 0})
        self.assertIs(uvtt["portals"][0]["closed"], True)
        self.assertEqual(uvtt["environment"]["lights"][0]["color"], "#ffcc88")
        self.assertEqual(uvtt["environment"]["lights"][0]["range"], 4)
        raw = (LEVELDB_SCENE / "assets" / "crypt.png").read_bytes()
        self.assertEqual(base64.b64decode(uvtt["image"]), raw)
        self.assertTrue(report["headline"].startswith("Unsupported "))
        self.assertGreater(
            report["counts"]["unsupported"] + report["counts"]["manual"],
            report["counts"]["native"],
        )
        loss_text = "\n".join(
            item["summary"]
            for grade in ("approximate", "manual", "unsupported")
            for item in report[grade]
        )
        self.assertIn("not on Arkenforge's documented import list", loss_text)
        loose = [item["path"] for item in report["approximate"] if item["code"] == "loose-import"]
        self.assertEqual(loose, ["assets/crypt.png", "assets/drip.wav"])
        for phrase in (
            "VaultToken",
            "Vault Keeper",
            "Vault note",
            "drip.wav",
            "note-vault",
            "region",
            "not executed",
            "notACoreField",
            "homebrewRule",
            "../../etc/passwd",
        ):
            self.assertIn(phrase, loss_text, phrase)
        blob = json.dumps(document)
        self.assertNotIn("writeFileSync", blob)
        self.assertNotIn("VaultToken", json.dumps(uvtt))
        self.assertNotIn("homebrewRule", json.dumps(uvtt))
        self.assertFalse((LEVELDB_SCENE / "packs" / "scenes" / "LOCK").exists())
        self.assertEqual(list(LEVELDB_SCENE.rglob("*.db")), [])
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_rebuilt_leveldb_scene_matches_committed_uvtt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "synthetic-leveldb-scene"
            (root / "assets").mkdir(parents=True)
            (root / "module.json").write_text((LEVELDB_SCENE / "module.json").read_text(encoding="utf-8"), encoding="utf-8")
            (root / "assets" / "crypt.png").write_bytes((LEVELDB_SCENE / "assets" / "crypt.png").read_bytes())
            (root / "assets" / "drip.wav").write_bytes((LEVELDB_SCENE / "assets" / "drip.wav").read_bytes())
            leveldb_fixture.build_scene(root / "packs" / "scenes")
            fresh = build_uvtt_slice(root, "scene-vault")
        committed = build_uvtt_slice(LEVELDB_SCENE, "scene-vault")
        self.assertEqual(fresh["uvtt"], committed["uvtt"])
        self.assertEqual(fresh["loss_report"]["counts"], committed["loss_report"]["counts"])
        self.assertFalse((LEVELDB_SCENE / "packs" / "scenes" / "LOCK").exists())
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_cli_writes_leveldb_scene_uvtt_file(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        raw = (LEVELDB_SCENE / "assets" / "crypt.png").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out" / "scene-vault.uvtt"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "forgebridge",
                    str(LEVELDB_SCENE),
                    "--uvtt-scene",
                    "scene-vault",
                    "--uvtt-out",
                    str(dest),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            envelope = json.loads(completed.stdout)
            written = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(written, envelope["uvtt"])
            self.assertTrue(envelope["loss_report"]["headline"].startswith("Unsupported "))
            self.assertEqual(validate(written, load_schema(repo_schema("uvtt-core.schema.json"))), [])
            self.assertNotIn("loss_report", written)
            self.assertEqual(base64.b64decode(written["image"]), raw)
            self.assertIn("VaultToken", envelope["loss_report"]["headline"] + json.dumps(envelope["loss_report"]))
        self.assertEqual(list(REPO.glob("**/*.uvtt")), [])
        self.assertFalse((LEVELDB_SCENE / "packs" / "scenes" / "LOCK").exists())
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_zipped_leveldb_scene_matches_the_unpacked_uvtt(self) -> None:
        zipped = build_uvtt_slice(LEVELDB_SCENE_ZIP, "scene-vault")
        unpacked = build_uvtt_slice(LEVELDB_SCENE, "scene-vault")
        self.assertEqual(validate(zipped["uvtt"], load_schema(repo_schema("uvtt-core.schema.json"))), [])
        self.assertEqual(validate(zipped["loss_report"], load_schema(repo_schema("uvtt-loss-report.schema.json"))), [])
        self.assertEqual(zipped["uvtt"], unpacked["uvtt"])
        self.assertEqual(zipped["loss_report"]["counts"], unpacked["loss_report"]["counts"])
        self.assertTrue(zipped["loss_report"]["headline"].startswith("Unsupported "))
        self.assertEqual(base64.b64decode(zipped["uvtt"]["image"]), (LEVELDB_SCENE / "assets" / "crypt.png").read_bytes())
        self.assertNotIn("writeFileSync", json.dumps(zipped))
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_cli_writes_uvtt_from_the_zipped_leveldb_scene(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "out" / "scene-vault.uvtt"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "forgebridge",
                    str(LEVELDB_SCENE_ZIP),
                    "--uvtt-scene",
                    "scene-vault",
                    "--uvtt-out",
                    str(dest),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            envelope = json.loads(completed.stdout)
            written = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(written, envelope["uvtt"])
            self.assertEqual(written, build_uvtt_slice(LEVELDB_SCENE, "scene-vault")["uvtt"])
            self.assertTrue(envelope["loss_report"]["headline"].startswith("Unsupported "))
            self.assertNotIn("loss_report", written)
        self.assertEqual(list(REPO.glob("**/*.uvtt")), [])
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_zip_entries_that_leave_the_archive_are_not_extracted(self) -> None:
        outside_name = "forgebridge-zip-escaped.js"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "hostile.zip"
            outside = root.parent / outside_name
            if outside.exists():
                outside.unlink()
            with zipfile.ZipFile(LEVELDB_SCENE_ZIP) as source, zipfile.ZipFile(archive, "w") as dest:
                for info in source.infolist():
                    dest.writestr(info, source.read(info))
                dest.writestr(
                    "../" + outside_name,
                    "require('fs').writeFileSync('/tmp/forgebridge-zip-executed','zip')",
                )
                dest.writestr(
                    "/tmp/forgebridge-abs.js",
                    "require('fs').writeFileSync('/tmp/forgebridge-abs.js','abs')",
                )
            document = build_uvtt_slice(archive, "scene-vault")
            self.assertFalse(outside.exists())
            self.assertFalse(any(root.rglob(outside_name)))
            self.assertFalse(Path("/tmp/forgebridge-abs.js").exists())
            self.assertFalse(Path("/tmp/forgebridge-zip-executed").exists())
            report = document["loss_report"]
            rejected = [item for item in report["unsupported"] if item["code"] == "rejected-zip-entry"]
            self.assertEqual(len(rejected), 2)
            joined = "\n".join(item["summary"] for item in rejected)
            self.assertIn("../" + outside_name, joined)
            self.assertIn("/tmp/forgebridge-abs.js", joined)
            self.assertNotIn("writeFileSync", json.dumps(document))
            self.assertEqual(document["uvtt"]["resolution"]["map_size"], {"x": 2, "y": 2})
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_zip_command_writes_uvtt_and_loose_image_audio(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        png = (LEVELDB_SCENE / "assets" / "crypt.png").read_bytes()
        wav = (LEVELDB_SCENE / "assets" / "drip.wav").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dest = root / "out" / "scene-vault.uvtt"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "forgebridge",
                    str(LEVELDB_SCENE_ZIP),
                    "--uvtt-scene",
                    "scene-vault",
                    "--uvtt-out",
                    str(dest),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            envelope = json.loads(completed.stdout)
            written = json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(written, envelope["uvtt"])
            self.assertEqual(base64.b64decode(written["image"]), png)
            self.assertNotIn("loss_report", written)
            self.assertEqual((dest.parent / "crypt.png").read_bytes(), png)
            self.assertEqual((dest.parent / "drip.wav").read_bytes(), wav)
            self.assertEqual(
                sorted(path.name for path in dest.parent.iterdir()),
                ["crypt.png", "drip.wav", "scene-vault.uvtt"],
            )
            self.assertFalse((root / "etc" / "passwd").exists())
            self.assertFalse((root / "passwd").exists())
            report = envelope["loss_report"]
            joined = "\n".join(item["summary"] for item in report["unsupported"])
            self.assertIn("../../etc/passwd", joined)
            self.assertIn("not on Arkenforge's documented import list", joined)
            self.assertNotIn("writeFileSync", completed.stdout)
        self.assertEqual(list(REPO.glob("**/*.uvtt")), [])
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_non_zip_file_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "module.zip"
            archive.write_bytes(b"not a package")
            with self.assertRaises(InventoryFatal) as caught:
                build_uvtt_slice(archive, "scene-crypt")
        self.assertIn("zip", str(caught.exception))


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
