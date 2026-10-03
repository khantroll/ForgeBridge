"""Validate inventory documents against the spike's JSON Schema.

The checker covers only the keywords the bundled schema uses. It is not a
general JSON Schema implementation.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


class InventoryFatal(Exception):
    """The package could not be inventoried."""


def repo_schema(filename: str) -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "schema" / filename
        if candidate.is_file():
            return candidate
    raise InventoryFatal(f"schema not found: {filename}")


def default_schema_path() -> Path:
    return repo_schema("inventory-0.1.schema.json")


def load_schema(path: Path | None = None) -> dict:
    schema_path = path or default_schema_path()
    try:
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InventoryFatal(f"schema unreadable: {exc}") from exc


def validate(instance: object, schema: dict) -> list[str]:
    errors: list[str] = []
    defs = schema.get("$defs", {})
    _check(instance, schema, "$", errors, defs)
    return errors


def _is_type(instance: object, kind: str) -> bool:
    if kind == "object":
        return isinstance(instance, dict)
    if kind == "array":
        return isinstance(instance, list)
    if kind == "string":
        return isinstance(instance, str)
    if kind == "boolean":
        return isinstance(instance, bool)
    if kind == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if kind == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if kind == "null":
        return instance is None
    return False


def _check(instance: object, schema: dict, path: str, errors: list[str], defs: dict) -> None:
    if "$ref" in schema:
        ref = schema["$ref"]
        prefix = "#/$defs/"
        if not isinstance(ref, str) or not ref.startswith(prefix) or ref[len(prefix):] not in defs:
            errors.append(f"{path}: unresolvable $ref")
            return
        _check(instance, defs[ref[len(prefix):]], path, errors, defs)
        return

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
        return

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not an allowed value")
        return

    types = schema.get("type")
    if isinstance(types, str):
        types = [types]
    if types is not None and not any(_is_type(instance, kind) for kind in types):
        errors.append(f"{path}: expected type {types}")
        return

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: does not match pattern")

    if _is_type(instance, "integer") and "minimum" in schema and instance < schema["minimum"]:
        errors.append(f"{path}: below minimum")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: more than maxItems")
        if "items" in schema:
            for index, item in enumerate(instance):
                _check(item, schema["items"], f"{path}/{index}", errors, defs)

    if isinstance(instance, dict) and (
        "properties" in schema or "required" in schema or "additionalProperties" in schema
    ):
        required = schema.get("required", [])
        props = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key}")
        for key, value in instance.items():
            child = f"{path}/{key}"
            if key in props:
                _check(value, props[key], child, errors, defs)
            elif additional is False:
                errors.append(f"{path}: additional property {key}")
            elif isinstance(additional, dict):
                _check(value, additional, child, errors, defs)
