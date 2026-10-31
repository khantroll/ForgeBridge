"""Developer-only CLI rehearsal with synthetic fixtures; never installs content.

Requires this repository's tests and requirements.txt. Creates only a new output
directory, retains command logs on failure and makes no native runtime claim.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'src'))
sys.path.insert(0, str(REPO / 'tests'))

from forgebridge.native_dependencies import check_metadata_references, merge_native
from forgebridge.scene_profile import fingerprint, load_profile
from test_scene_profile import setup_profiles


def rehearse(destination):
    root = Path(destination).absolute()
    if root.exists() or root.is_symlink():
        raise ValueError('Choose a new rehearsal output directory; nothing is overwritten')
    root.mkdir(parents=True)
    source = root / 'synthetic inputs'
    source.mkdir()
    profiles = setup_profiles(source)
    source_hash = fingerprint(source)
    cwd = root / 'unrelated working directory'
    cwd.mkdir()
    logs = root / 'logs'
    logs.mkdir()
    env = dict(os.environ, PYTHONPATH=str(REPO / 'src'), PYTHONUTF8='1')
    commands = []

    def cli(module, *args, expected=0):
        command = [sys.executable, '-m', module, *map(str, args)]
        completed = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                   text=True, encoding='utf-8', timeout=120)
        index = len(commands)
        (logs / f'{index:02d}.stdout.txt').write_text(completed.stdout, encoding='utf-8')
        (logs / f'{index:02d}.stderr.txt').write_text(completed.stderr, encoding='utf-8')
        commands.append({'command': command, 'exit': completed.returncode, 'expected': expected})
        (logs / 'commands.json').write_text(json.dumps(commands, indent=2)+'\n', encoding='utf-8')
        if completed.returncode != expected:
            raise ValueError(f'Command {index} exited {completed.returncode}, expected {expected}; inspect {logs}')
        return completed

    # Exercise capture's actual public CLI before moving the self-contained bundle.
    relocated = root / 'relocated profiles'
    relocated.mkdir()
    for sid, profile in zip(('A', 'B', 'Zero'), profiles):
        temporary = root / ('portable-' + sid)
        cli('forgebridge.native_capture', '--profile', profile, '--out', temporary)
        shutil.move(temporary, relocated / sid)
    offline = root / 'original inputs offline'
    source.rename(offline)  # Only the newly created synthetic fixture tree moves.
    rows, combined = [], {}
    for sid in ('A', 'B', 'Zero'):
        folder = relocated / sid
        profile = folder / 'scene-profile.json'
        _, paths, _ = load_profile(profile)
        if not all(path.is_relative_to(folder) for path in paths.values()):
            raise ValueError('Relocated profile escaped its own bundle')
        audited = json.loads(cli('forgebridge.native_capture', '--export',
            folder/'capture/native.zip', '--audit').stdout)
        if not audited['ok']:
            raise ValueError('Native closure audit failed')
        preflight = json.loads(cli('forgebridge.package', '--profile', profile, '--preflight').stdout)
        output = root / (sid + '-scene.zip')
        cli('forgebridge.package', '--profile', profile, '--out', output)
        with zipfile.ZipFile(output) as archive:
            files = {n: archive.read(n) for n in archive.namelist()}
        report = json.loads(files['conversion-report.json'])
        expected = (0, 0) if sid == 'Zero' else (1, 2)
        actual = (report['counts']['native_tokens'], report['counts']['unsupported_tokens'])
        if actual != expected or preflight['supported_tokens'] != expected[0]:
            raise ValueError('Token outcome counts do not reconcile for ' + sid)
        references = check_metadata_references(files)
        merge_native(combined, {n: d for n, d in files.items() if n.startswith('MyAssets/')})
        digest = fingerprint(output)
        cli('forgebridge.package', '--profile', profile, '--out', output, expected=1)
        if fingerprint(output) != digest:
            raise ValueError('Rejected overwrite modified an existing package')
        # Alter only this portable copy, verify refusal, then restore exact bytes.
        companion = paths['source.companion']
        original = companion.read_bytes()
        try:
            companion.write_bytes(original + b'\n')
            rejected = root / (sid + '-changed-input.zip')
            result = cli('forgebridge.package', '--profile', profile, '--out', rejected, expected=1)
            if rejected.exists() or 'mismatch' not in result.stderr.lower():
                raise ValueError('Changed-input failure did not preserve the output boundary')
        finally:
            companion.write_bytes(original)
        rows.append({'scene': sid, 'map': report['native_map'],
                     'native_tokens': actual[0], 'rejected_tokens': actual[1],
                     'closed_references': references, 'package_sha256': digest,
                     'native_payload_sha256': hashlib.sha256(b''.join(
                         n.encode() + b'\0' + hashlib.sha256(d).digest()
                         for n, d in sorted(files.items()) if n.startswith('MyAssets/'))).hexdigest()})
    if fingerprint(offline) != source_hash:
        raise ValueError('Original synthetic inputs changed')
    snapshot = root / 'static snapshot' / 'MyAssets'
    snapshot.mkdir(parents=True)
    for name, data in combined.items():
        path = snapshot.parent / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    review_args = ['--snapshot-root', snapshot, '--static-snapshot']
    for sid in ('A', 'B', 'Zero'):
        review_args.extend(['--package', root / (sid + '-scene.zip')])
    identical_review = json.loads(cli('forgebridge.install_review', *review_args).stdout)
    if identical_review['counts']['identical'] != len(combined) or not identical_review['ok']:
        raise ValueError('Snapshot review did not reconcile identical package contents')
    edited = next(snapshot.parent / name for name in sorted(combined) if name.endswith('.rwnote'))
    original = edited.read_bytes()
    try:
        edited.write_bytes(b'manual user edits')
        conflict_review = json.loads(cli('forgebridge.install_review', *review_args, expected=1).stdout)
        if conflict_review['counts']['conflict'] != 1 or edited.read_bytes() != b'manual user edits':
            raise ValueError('Read-only conflict review did not preserve user edits')
    finally:
        edited.write_bytes(original)
    result = {'format': 'forgebridge.operator-rehearsal', 'version': 1, 'status': 'PASS',
              'scope': 'synthetic public CLI/file checks; no install or native runtime validation',
              'source_unchanged': True, 'commands': len(commands), 'scenes': rows,
              'combined_closed_references': check_metadata_references(combined),
              'original_paths_unavailable_during_build': True,
              'install_review': {'identical': identical_review['counts'],
                                 'manual_edit': conflict_review['counts'], 'writes': 'none'},
              'runtime_validation': 'not performed'}
    (root / 'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, help='New directory for synthetic inputs, outputs and logs')
    args = parser.parse_args()
    print(json.dumps(rehearse(args.out), indent=2))


if __name__ == '__main__':
    main()
