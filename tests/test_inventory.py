"""Inventory schema and hostile-input tests."""

from __future__ import annotations

import hashlib
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
LEVELDB = REPO / "fixtures" / "leveldb-pointer"
sys.path.insert(0, str(SRC))

from forgebridge.inventory import inventory_path  # noqa: E402
from forgebridge.validate import load_schema, validate  # noqa: E402

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


def _clear_markers() -> None:
    for marker in MARKERS:
        path = Path(marker)
        if path.exists():
            path.unlink()


def _assert_not_executed(test: unittest.TestCase, document: dict) -> None:
    def walk(node: object) -> None:
        if isinstance(node, dict):
            if "executed" in node:
                test.assertIs(node["executed"], False)
            if "interpreted" in node:
                test.assertIs(node["interpreted"], False)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(document)
    for marker in MARKERS:
        test.assertFalse(Path(marker).exists(), marker)


class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        _clear_markers()

    def tearDown(self) -> None:
        _clear_markers()

    def test_synthetic_module_matches_schema_and_keeps_unknown_fields(self) -> None:
        document = inventory_path(FIXTURE)
        errors = validate(document, load_schema())
        self.assertEqual(errors, [], errors)
        _assert_not_executed(self, document)

        counts = document["counts"]["documents_by_type"]
        self.assertEqual(counts["Scene"], 1)
        self.assertEqual(counts["Actor"], 1)
        self.assertEqual(counts["Macro"], 2)
        self.assertEqual(sum(counts.values()), len(document["documents"]))
        self.assertIn("maps", document["counts"]["domains_present"])
        self.assertIn("behaviors", document["counts"]["domains_present"])
        self.assertIn("provenance", document["counts"]["domains_present"])

        scene = next(item for item in document["documents"] if item["id"] == "scene-crypt")
        self.assertEqual(scene["door_codes"], [1])
        self.assertEqual(scene["embedded_counts"]["Wall"], 1)
        self.assertEqual(scene["embedded_counts"]["RegionBehavior"], 1)
        self.assertIn("forgebridge-synthetic", scene["flag_scopes"])
        self.assertEqual(scene["retained_fields"]["notACoreField"]["reason"], "must be retained")
        self.assertIn("img", scene["retained_fields"])

        actor = next(item for item in document["documents"] if item["id"] == "actor-mummy")
        self.assertEqual(actor["retained_fields"]["_unpinned_source"]["homebrewRule"], {"dc": 15})
        self.assertIn("homebrewRule", json.dumps(document))
        self.assertEqual(document["provenance"]["manifest_unmapped"]["notAFoundryManifestKey"], {"kept": True})

        crypt_refs = next(asset for asset in document["assets"] if asset["ref"] == "assets/crypt.png")
        self.assertTrue(crypt_refs["present_in_package"])
        self.assertFalse(any(ref["field"] == "command" or ref["field"].endswith(".command") for ref in crypt_refs["referenced_by"]))

        hostile = next(asset for asset in document["assets"] if asset["ref"] == "../../etc/passwd")
        self.assertTrue(hostile["hostile"])
        self.assertFalse(hostile["present_in_package"])
        missing = next(asset for asset in document["assets"] if asset["ref"] == "assets/no-such.webp")
        self.assertFalse(missing["present_in_package"])
        external = next(asset for asset in document["assets"] if asset["external"])
        self.assertEqual(external["kind"], "external")
        self.assertTrue(any(asset["ref"] == "assets/orphan.png" and asset["referenced_by"] == [] for asset in document["assets"]))

        yaml_pack = next(pack for pack in document["packs"] if pack["name"] == "unsafe-yaml")
        self.assertEqual(yaml_pack["storage"], "yaml")
        self.assertFalse(yaml_pack["decoded"])
        self.assertEqual(yaml_pack["document_count"], 0)

        codes = {item["code"] for item in document["diagnostics"]}
        self.assertIn("package-script-not-executed", codes)
        self.assertIn("yaml-not-decoded", codes)
        self.assertIn("active-content-not-interpreted", codes)
        self.assertIn("script-body-not-parsed", codes)
        self.assertIn("hostile-asset-reference", codes)
        self.assertNotIn("error", {item["severity"] for item in document["diagnostics"]})

        behaviors = document["behaviors"]
        self.assertTrue(all(item["executed"] is False and item["interpreted"] is False for item in behaviors))
        payloads = json.dumps([item["payload"] for item in behaviors])
        self.assertIn("/tmp/forgebridge-macro-executed", payloads)
        self.assertIn("/tmp/forgebridge-region-executed", payloads)
        script = next(item for item in document["provenance"]["scripts_not_executed"] if item["path"] == "scripts/trap.js")
        digest = hashlib.sha256((FIXTURE / "scripts" / "trap.js").read_bytes()).hexdigest()
        self.assertEqual(script["sha256"], digest)
        self.assertIn("/tmp/forgebridge-script-executed", script["preview"])

    def test_schema_rejects_executed_behavior(self) -> None:
        document = inventory_path(FIXTURE)
        document["behaviors"][0]["executed"] = True
        errors = validate(document, load_schema())
        self.assertTrue(errors)
        for marker in MARKERS:
            self.assertFalse(Path(marker).exists(), marker)

    def test_leveldb_pack_is_not_decoded_or_executed(self) -> None:
        document = inventory_path(LEVELDB)
        self.assertEqual(validate(document, load_schema()), [])
        pack = document["packs"][0]
        self.assertEqual(pack["storage"], "leveldb")
        self.assertFalse(pack["decoded"])
        self.assertEqual(pack["document_count"], 0)
        self.assertEqual(document["documents"], [])
        blob = json.dumps(document)
        self.assertNotIn("should-not-import", blob)
        self.assertIn("leveldb-not-decoded", {item["code"] for item in document["diagnostics"]})
        _assert_not_executed(self, document)

    def test_zip_matches_directory_and_rejects_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "synthetic-module.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                for path in FIXTURE.rglob("*"):
                    if path.is_file():
                        handle.write(path, Path("synthetic-module") / path.relative_to(FIXTURE))
                handle.writestr(
                    "synthetic-module/../escape.js",
                    "require('fs').writeFileSync('/tmp/forgebridge-zip-executed','zip')\n",
                )
                handle.writestr("/tmp/forgebridge-abs.js", "require('fs').writeFileSync('/tmp/forgebridge-zip-executed','abs')\n")
                handle.writestr(
                    "synthetic-module/packs/../../sneak.js",
                    "require('fs').writeFileSync('/tmp/forgebridge-zip-executed','sneak')\n",
                )
            zipped = inventory_path(archive)
            direct = inventory_path(FIXTURE)
            self.assertEqual(validate(zipped, load_schema()), [])
            self.assertEqual(
                {item["id"] for item in zipped["documents"]},
                {item["id"] for item in direct["documents"]},
            )
            self.assertEqual(zipped["provenance"]["input_form"], "zip")
            self.assertEqual(zipped["provenance"]["source_name"], "synthetic-module")
            self.assertIn("rejected-zip-entry", {item["code"] for item in zipped["diagnostics"]})
            self.assertFalse((Path(tmp) / "escape.js").exists())
            _assert_not_executed(self, zipped)

    def test_symlink_pack_is_not_followed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "synthetic-module"
            outside = Path(tmp) / "outside.db"
            (root / "packs").mkdir(parents=True)
            outside.write_text('{"_id":"leaked","name":"Leaked secret"}\n', encoding="utf-8")
            (root / "module.json").write_text(
                json.dumps({
                    "id": "synthetic-module",
                    "title": "Symlink",
                    "version": "0.0.1",
                    "packs": [{"name": "actors", "label": "Actors", "path": "packs/actors.db", "type": "Actor", "system": "synthetic-core"}],
                }),
                encoding="utf-8",
            )
            try:
                (root / "packs" / "actors.db").symlink_to(outside)
            except OSError as exc:
                if getattr(exc, "winerror", None) != 1314:
                    raise
                self.skipTest("Windows symlink creation privilege unavailable (WinError 1314)")
            document = inventory_path(root)
            self.assertNotIn("Leaked secret", json.dumps(document))
            self.assertIn("symlink-skipped", {item["code"] for item in document["diagnostics"]})
            self.assertEqual(document["documents"], [])

    def test_world_folder_reads_text_collection_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "synthetic-world"
            (root / "data" / "mystery").mkdir(parents=True)
            (root / "data" / "actors.db").write_text(
                json.dumps({"_id": "actor-world", "name": "World actor", "type": "character"}) + "\n",
                encoding="utf-8",
            )
            (root / "data" / "mystery" / "CURRENT").write_text("MANIFEST-000001\n", encoding="utf-8")
            (root / "data" / "mystery" / "000001.ldb").write_bytes(b'{"_id":"hidden","name":"Hidden"}\n')
            (root / "world.json").write_text(
                json.dumps({
                    "id": "synthetic-world",
                    "title": "Synthetic World",
                    "type": "world",
                    "version": "0.0.1",
                    "system": "synthetic-core",
                    "systemVersion": "0.0.1",
                    "coreVersion": "14",
                }),
                encoding="utf-8",
            )
            document = inventory_path(root)
            self.assertEqual(validate(document, load_schema()), [])
            self.assertEqual(document["provenance"]["package_type"], "world")
            self.assertEqual(document["provenance"]["system"], "synthetic-core")
            self.assertEqual([item["id"] for item in document["documents"]], ["actor-world"])
            self.assertNotIn("Hidden", json.dumps(document["documents"]))
            self.assertIn("unknown-world-collection", {item["code"] for item in document["diagnostics"]})

    def test_json_array_pack_and_javascript_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "json-pack"
            (root / "packs").mkdir(parents=True)
            (root / "packs" / "tables.json").write_text(
                json.dumps([{"_id": "table-json", "name": "JSON table", "results": []}]),
                encoding="utf-8",
            )
            (root / "module.json").write_text(
                json.dumps({
                    "id": "json-pack",
                    "title": "JSON pack",
                    "version": "0.0.1",
                    "packs": [{"name": "tables", "label": "Tables", "path": "packs/tables.json", "type": "RollTable"}],
                }),
                encoding="utf-8",
            )
            document = inventory_path(root)
            self.assertEqual(validate(document, load_schema()), [])
            self.assertEqual(document["documents"][0]["id"], "table-json")
            self.assertEqual(document["documents"][0]["storage"], "json")

            hostile = Path(tmp) / "not-json"
            hostile.mkdir()
            (hostile / "module.json").write_text(
                "require('fs').writeFileSync('/tmp/forgebridge-macro-executed','manifest')\n",
                encoding="utf-8",
            )
            with self.assertRaises(Exception):
                inventory_path(hostile)
            self.assertFalse(Path("/tmp/forgebridge-macro-executed").exists())

    def test_cli_prints_schema_valid_inventory(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        completed = subprocess.run(
            [sys.executable, "-m", "forgebridge", str(FIXTURE)],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        document = json.loads(completed.stdout)
        self.assertEqual(validate(document, load_schema()), [])
        _assert_not_executed(self, document)
        missing = subprocess.run(
            [sys.executable, "-m", "forgebridge", str(FIXTURE / "missing.zip")],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(missing.returncode, 1)
        self.assertEqual(missing.stdout, "")

    def test_reader_source_has_no_dynamic_execution(self) -> None:
        import ast
        banned = ("eval(", "exec(", "subprocess", "os.system", "importlib", "pickle", "yaml.load")
        for path in (SRC / "forgebridge").glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in banned:
                self.assertNotIn(token, text, f"{path.name} contains {token}")
            # Pure URL parsing is permitted; network-capable imports are not.
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, ast.Import):
                    self.assertFalse(any(a.name.startswith('urllib') for a in node.names))
                elif isinstance(node, ast.ImportFrom) and (node.module or '').startswith('urllib'):
                    self.assertEqual(node.module, 'urllib.parse')
                    self.assertTrue({a.name for a in node.names} <= {'unquote', 'urlsplit'})


if __name__ == "__main__":
    unittest.main()
