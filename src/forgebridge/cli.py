"""Command-line entry for inventory and the one-scene UVTT file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from forgebridge.inventory import inventory_path
from forgebridge.notes import render_notes_text
from forgebridge.uvtt import build_uvtt_slice, scene_loose_files
from forgebridge.validate import InventoryFatal, load_schema, repo_schema, validate
from forgebridge.version import get_version


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == 'convert':
        from forgebridge.convert import main as convert_main
        return convert_main(argv[1:])
    if argv and argv[0] == 'install':
        from forgebridge.installer import main as install_main
        return install_main(argv[1:])
    if argv and argv[0] == 'gui':
        from forgebridge.gui import main as gui_main
        return gui_main(argv[1:])
    parser = argparse.ArgumentParser(
        prog="forgebridge",
        description=(
            "Inventory a Foundry VTT module folder or zip, or write one scene as UVTT JSON "
            "plus a graded loss report. Does not execute imported JavaScript, macros, or HTML."
        ),
    )
    parser.add_argument('--version', action='version', version='ForgeBridge ' + get_version())
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
        help="Write this scene id as UVTT JSON plus a graded loss report. Reads a module folder or a .zip archive.",
    )
    parser.add_argument(
        "--uvtt-out",
        metavar="FILE",
        help=(
            "After validation, write the UVTT object to FILE and the scene's importable "
            "image/audio files, a .forgebridge.json source/journal sidecar, and a .notes.txt GM reference beside it. Stdout remains the envelope with the loss report."
        ),
    )
    args = parser.parse_args(argv)
    if args.uvtt_out and not args.uvtt_scene:
        print("--uvtt-out requires --uvtt-scene", file=sys.stderr)
        return 1
    if args.uvtt_scene:
        return _uvtt(Path(args.package), args.uvtt_scene, compact=args.compact, uvtt_out=args.uvtt_out)
    return _inventory(Path(args.package), schema=args.schema, compact=args.compact)


def _inventory(package: Path, schema: str | None, compact: bool) -> int:
    try:
        document = inventory_path(package)
        loaded = load_schema(Path(schema) if schema else None)
    except InventoryFatal as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return _emit(document, [(loaded, "inventory output did not match the IR schema")], compact)


def _uvtt(package: Path, scene_id: str, compact: bool, uvtt_out: str | None) -> int:
    try:
        document = build_uvtt_slice(package, scene_id)
        uvtt_schema = load_schema(repo_schema("uvtt-core.schema.json"))
        loss_schema = load_schema(repo_schema("uvtt-loss-report.schema.json"))
    except InventoryFatal as exc:
        print(str(exc), file=sys.stderr)
        return 1
    checks = [
        (uvtt_schema, "uvtt output did not match the UVTT core schema", document["uvtt"]),
        (loss_schema, "loss report did not match its schema", document["loss_report"]),
    ]
    if _reject(checks, document):
        return 2
    if uvtt_out:
        try:
            dest = Path(uvtt_out)
            loose = scene_loose_files(package, scene_id)
            targets = [dest, dest.with_suffix('.forgebridge.json'), dest.with_suffix('.notes.txt')]
            targets += [dest.parent / name for name, _ in loose]
            if len({str(p.absolute()).casefold() for p in targets}) != len(targets):
                raise OSError('Output names collide; select a distinct UVTT filename')
            for target in targets:
                if target.exists() or any(p.is_symlink() or p.is_junction() for p in (target, *target.absolute().parents)):
                    raise OSError(f'refusing existing or linked output: {target}')
            _write_uvtt_file(dest, document["uvtt"])
            _write_loose_files(dest.parent, loose)
            _write_uvtt_file(dest.with_suffix(".forgebridge.json"), {
                "schema_version": "1.0",
                "scene_id": scene_id,
                "source_scene": document["source_scene"],
                "scene_notes": document["scene_notes"],
                "loss_report": document["loss_report"],
            })
            notes_dest = dest.with_suffix('.notes.txt')
            if notes_dest.is_symlink() or notes_dest.is_dir():
                raise OSError(f'refusing to write notes reference to {notes_dest}')
            with notes_dest.open('x', encoding='utf-8') as stream:
                stream.write(render_notes_text(document['scene_notes']))
        except (OSError, InventoryFatal) as exc:
            print(f"UVTT file was not written: {exc}", file=sys.stderr)
            return 1
    _print_json(document, compact)
    return 0


def _write_loose_files(directory: Path, files: list[tuple[str, bytes]]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    root = directory.resolve()
    for name, data in files:
        if Path(name).name != name or name in {"", ".", ".."}:
            raise InventoryFatal(f"loose asset name was rejected: {name}")
        target = directory / name
        try:
            target.resolve().relative_to(root)
        except (OSError, ValueError) as exc:
            raise InventoryFatal(f"loose asset path leaves the output directory: {name}") from exc
        if target.is_symlink():
            raise InventoryFatal(f"refusing to write through a symlink: {name}")
        with target.open('xb') as stream:
            stream.write(data)


def _write_uvtt_file(path: Path, uvtt: dict) -> None:
    if path.is_symlink():
        raise OSError(f"refusing to write through a symlink: {path}")
    if path.exists() and path.is_dir():
        raise OSError(f"{path} is a directory")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(uvtt, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    with path.open('x', encoding='utf-8') as stream:
        stream.write(text)


def _emit(document: dict, checks: list, compact: bool) -> int:
    if _reject(checks, document):
        return 2
    _print_json(document, compact)
    return 0


def _reject(checks: list, document: dict) -> bool:
    for item in checks:
        schema = item[0]
        label = item[1]
        target = item[2] if len(item) > 2 else document
        errors = validate(target, schema)
        if errors:
            print(label, file=sys.stderr)
            for error in errors:
                print(error, file=sys.stderr)
            return True
    return False


def _print_json(document: dict, compact: bool) -> None:
    json.dump(document, sys.stdout, indent=None if compact else 2, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
