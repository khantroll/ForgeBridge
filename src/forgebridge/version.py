"""Installed package version, with an embedded frozen-build fallback."""
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path


def get_version():
    try:
        return version('forgebridge')
    except PackageNotFoundError:
        try:
            return json.loads(Path(__file__).with_name('build-info.json').read_text(encoding='utf-8'))['version']
        except (OSError, ValueError, KeyError):
            return '0.12.0'
