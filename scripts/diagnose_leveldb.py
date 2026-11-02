"""Bounded file-only LevelDB experiment; never retry a failed operation.

Each trial uses a distinct new database/copy. Preserve all output, including
failed copies, for inspection. No campaigns, installed assets or source fixtures
are opened by LevelDB, modified, or deleted.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import time

import plyvel_next as plyvel

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from forgebridge.leveldb import LevelDBResult, _copy_flat, _open_and_decode
from windows_replace_probe import probe, process_context


def hashes(root):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.iterdir()) if p.is_file() and not p.is_symlink()}


def run(destination, trials):
    fixture = Path(__file__).resolve().parents[1] / 'fixtures/synthetic-leveldb-scene/packs/scenes'
    destination = Path(destination).absolute()
    if (destination.resolve().is_relative_to(fixture.resolve())
            or fixture.resolve().is_relative_to(destination.resolve())):
        raise ValueError('Choose an output outside the source fixture and its ancestors')
    destination.mkdir(parents=True, exist_ok=False)
    before = hashes(fixture)
    report = {'format': 'forgebridge.leveldb-diagnostic', 'version': 1,
              'python': platform.python_version(), 'platform': platform.platform(),
              'binding': importlib.metadata.version('plyvel-next'),
              'logical_processors': os.cpu_count(), 'trials_per_case': trials,
              'source_hashes': before, 'operations': [],
              'windows_process_context': process_context(),
              'scope': 'Isolated experiments, no production retry or runtime-validation claim'}
    def checkpoint():
        (destination / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    checkpoint()
    cases = ['create', 'copied-open', 'replace-control', 'reader-copy-open']
    if os.name == 'nt':
        cases.extend(['native-replace', 'native-held-target'])
    report['cases'] = cases
    report['native_probe_scope'] = 'Upstream-style MoveFileA/ReplaceFileA comparison; installed wheel build identity not established'
    for case in cases:
        for trial in range(trials):
            work = destination / f'{case}-{trial:02}'
            work.mkdir()
            row = {'case': case, 'trial': trial + 1, 'status': 'FAIL'}
            started = time.monotonic()
            db = None
            try:
                if case.startswith('native-'):
                    row.update(probe(work, hold_target=case == 'native-held-target'))
                elif case == 'reader-copy-open':
                    result = LevelDBResult()
                    _copy_flat(fixture, work / 'db', result, 64 * 1024 * 1024)
                    row['copied_hashes_match'] = hashes(work / 'db') == before
                    if not row['copied_hashes_match']:
                        raise ValueError('Reader copy hashes differ before open')
                    _open_and_decode(work / 'db', result, max_entries=10000, max_value_bytes=64*1024*1024)
                    row['diagnostics'] = result.diagnostics
                    row['documents'] = len(result.documents)
                    if not result.opened or not result.documents:
                        raise ValueError('Reader copy open/decode failed: ' + str(result.diagnostics))
                elif case == 'replace-control':
                    # Same path family as LevelDB's CURRENT publication, but
                    # ordinary Python replacement, no database binding involved.
                    (work / 'CURRENT').write_bytes(b'old\n')
                    (work / '000002.dbtmp').write_bytes(b'new\n')
                    os.replace(work / '000002.dbtmp', work / 'CURRENT')
                    if (work / 'CURRENT').read_bytes() != b'new\n':
                        raise ValueError('Replacement bytes differ')
                else:
                    path = work / 'db'
                    if case == 'copied-open':
                        path.mkdir()
                        for name in before:
                            shutil.copyfile(fixture / name, path / name)
                        if hashes(path) != before:
                            raise ValueError('Copied fixture hashes differ before open')
                    db = plyvel.DB(str(path), create_if_missing=case == 'create')
                    if case == 'create':
                        db.put(b'!scenes!diagnostic', b'{"_id":"diagnostic"}', sync=True)
                        if db.get(b'!scenes!diagnostic') != b'{"_id":"diagnostic"}':
                            raise ValueError('Created value differs')
                    else:
                        row['entries'] = sum(1 for _ in db)
                        if not row['entries']:
                            raise ValueError('Copied fixture decoded no entries')
                    db.close()
                    db = None
                row['status'] = 'PASS'
            except (plyvel.Error, OSError, ValueError) as exc:
                row['error_type'] = type(exc).__name__
                row['error'] = str(exc)  # Full detail kept locally, not truncated.
                row.update(getattr(exc, 'details', {}))
            finally:
                if db is not None:
                    db.close()
                row['seconds'] = round(time.monotonic() - started, 4)
                report['operations'].append(row)
                checkpoint()
    report['source_unchanged'] = hashes(fixture) == before
    report['totals'] = {case: {status: sum(r['case'] == case and r['status'] == status
                                               for r in report['operations'])
                               for status in ('PASS', 'FAIL')}
                        for case in cases}
    checkpoint()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, help='New output directory; all evidence retained')
    parser.add_argument('--trials', type=int, choices=range(1, 31), default=10)
    args = parser.parse_args()
    report = run(args.out, args.trials)
    print(json.dumps({'totals': report['totals'], 'source_unchanged': report['source_unchanged']}, indent=2))
    return int(not report['source_unchanged'] or any(r['status'] == 'FAIL' for r in report['operations']))


if __name__ == '__main__':
    raise SystemExit(main())
