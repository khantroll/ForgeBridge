"""Command-line entry for inventory and the one-scene UVTT slice."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from forgebridge.inventory import inventory_path
from forgebridge.uvtt import build_uvtt_slice
from forgebridge.validate import InventoryFatal, load_schema, repo_schema, validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="forgebridge",
        description=(
            "Inventory a Foundry VTT module folder or zip, or write one scene as UVTT JSON "
            "plus a loss report. Does not execute imported JavaScript, macros, or HTML."
        ),
    )
    parser.add_argument("package", help="Path to a module directory or .zip archive")
    parser.add_argument("--compact", action="store_true", help="Print JSON on one line")
    parser.add_argument(
        "--schema",
        default=None,
        help="Inventory schema path (defaults to the schema shipped with this repo)",
    )
    parser.add_argument(
        "--uvtt-scene",
        metavar="SCENE_ID",
        help="Write this scene id as UVTT JSON plus a loss report. Reads a module folder.",
    )
    args = parser.parse_args(argv)
    if args.uvtt_scene:
        return _uvtt(Path(args.package), args.uvtt_scene, compact=args.compact)
    return _inventory(Path(args.package), schema=args.schema, compact=args.compact)


def _inventory(package: Path, schema: str | None, compact: bool) -> int:
    try:
        document = inventory_path(package)
        loaded = load_schema(Path(schema) if schema else None)
    except InventoryFatal as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return _emit(document, [(loaded, "inventory output did not match the IR schema")], compact)


def _uvtt(package: Path, scene_id: str, compact: bool) -> int:
    try:
        document = build_uvtt_slice(package, scene_id)
        uvtt_schema = load_schema(repo_schema("uvtt-core.schema.json"))
        loss_schema = load_schema(repo_schema("uvtt-loss-report.schema.json"))
    except InventoryFatal as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return _emit(
        document,
        [
            (uvtt_schema, "uvtt output did not match the UVTT core schema", document["uvtt"]),
            (loss_schema, "loss report did not match its schema", document["loss_report"]),
        ],
        compact,
    )


def _emit(document: dict, checks: list, compact: bool) -> int:
    for item in checks:
        schema = item[0]
        label = item[1]
        target = item[2] if len(item) > 2 else document
        errors = validate(target, schema)
        if errors:
            print(label, file=sys.stderr)
            for error in errors:
                print(error, file=sys.stderr)
            return 2
    json.dump(document, sys.stdout, indent=None if compact else 2, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    return 0
