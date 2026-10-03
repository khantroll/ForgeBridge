"""Command-line entry for the inventory spike."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from forgebridge.validate import InventoryFatal, load_schema, validate
from forgebridge.inventory import inventory_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="forgebridge",
        description=(
            "Inventory a Foundry VTT module folder or zip. "
            "Prints JSON. Does not execute imported JavaScript, macros, or HTML."
        ),
    )
    parser.add_argument("package", help="Path to a module directory or .zip archive")
    parser.add_argument("--compact", action="store_true", help="Print JSON on one line")
    parser.add_argument(
        "--schema",
        default=None,
        help="Inventory schema path (defaults to the schema shipped with this repo)",
    )
    args = parser.parse_args(argv)

    try:
        document = inventory_path(Path(args.package))
        schema = load_schema(Path(args.schema) if args.schema else None)
    except InventoryFatal as exc:
        print(str(exc), file=sys.stderr)
        return 1

    errors = validate(document, schema)
    if errors:
        print("inventory output did not match the IR schema", file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        return 2

    json.dump(document, sys.stdout, indent=None if args.compact else 2, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    return 0
