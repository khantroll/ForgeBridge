"""Test extracted executables with no Python on their PATH; synthetic assets only."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import zipfile


def pdf():
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Count 2 /Kids [3 0 R 5 0 R] >>']
    for i in range(2):
        drawing = (b'1 0 0' if i == 0 else b'0 0 1') + b' rg 0 0 200 100 re f'
        objects.extend([f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 100] /Resources << >> /Contents {4+2*i} 0 R >>'.encode(),
                        f'<< /Length {len(drawing)} >>\nstream\n'.encode() + drawing + b'\nendstream'])
    data, offsets = b'%PDF-1.4\n', [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(data)); data += f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n'
    start = len(data)
    data += f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode()
    data += b''.join(f'{v:010} 00000 n \n'.encode() for v in offsets[1:])
    return data + f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode()


def smoke(archive, fixture, out, *, skip_install=False):
    out = Path(out).absolute()
    if out.exists(): raise ValueError('Smoke directory must be new')
    out.mkdir(parents=True)
    env = dict(os.environ)
    for key in ('PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV'): env.pop(key, None)
    env['PATH'] = str(Path(os.environ['SystemRoot']) / 'System32')
    env['LOCALAPPDATA'] = str(out / 'local-appdata')
    env['PYTHONIOENCODING'] = 'utf-8'
    assert shutil.which('python', path=env['PATH']) is None
    relocated = out / 'relocated app with spaces'
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            p = PurePosixPath(name)
            assert not p.is_absolute() and '..' not in p.parts and ':' not in name
        z.extractall(relocated)
    app = relocated / 'ForgeBridge'
    cli, gui = app / 'forgebridge-cli.exe', app / 'ForgeBridge.exe'
    commands = []
    def run(exe, *args, as_json=True):
        result = subprocess.run([str(exe), *map(str, args)], cwd=out, env=env,
                                capture_output=True, text=True, encoding='utf-8', timeout=180)
        index = len(commands) + 1
        (out / f'command-{index}.stdout.txt').write_text(result.stdout, encoding='utf-8')
        (out / f'command-{index}.stderr.txt').write_text(result.stderr, encoding='utf-8')
        commands.append({'exe': exe.name, 'args': list(map(str, args)), 'exit': result.returncode})
        assert result.returncode == 0, f'{exe.name}: {result.stderr}\n{result.stdout}'
        return json.loads(result.stdout) if as_json else result.stdout.strip()
    version = run(cli, '--version', as_json=False)
    assert version.startswith('ForgeBridge ')
    assert Path(archive).name == f"ForgeBridge-{version.split(' ', 1)[1]}-windows-x64.zip"
    inventoried = run(cli, Path(fixture).absolute())
    assert inventoried['generator']['version'] == version.split(' ', 1)[1]
    assert inventoried['ir_version'] == '0.1.0'
    # Exact public command with the repository's untouched synthetic fixture.
    plain = run(cli, 'convert', Path(fixture).absolute(), '--out', out / 'fixture-output')
    assert plain['status'] == 'PASS' and plain['pdf_mode'] == 'pages'
    native_zip = out / 'fixture-output/scene-001/native-package.zip'
    assert native_zip.is_file()
    # Exercise the actual pdfium DLL, not just import availability.
    source = out / 'pdf-source'; shutil.copytree(fixture, source)
    (source / 'assets/standalone.pdf').write_bytes(pdf())
    journal_file = source / 'packs/journal.db'
    journal = json.loads(journal_file.read_text())
    journal['pages'].append({'_id': 'pdf', 'name': 'Bundled PDF', 'type': 'pdf', 'src': 'assets/standalone.pdf'})
    journal_file.write_text(json.dumps(journal))
    rendered = run(cli, 'convert', source, '--out', out / 'pdf-output')
    assert rendered['scenes'][0]['native_report']['counts']['native_pdf_pages'] == 2
    # The build interpreter only prepares the fixture; the EXE reads LevelDB.
    import plyvel_next
    level = out / 'leveldb-source'; shutil.copytree(source, level)
    scene = json.loads((level / 'packs/scenes.db').read_text())
    scene = {k: scene[k] for k in ('_id', 'name', 'width', 'height', 'img', 'grid')}
    manifest_file = level / 'module.json'; manifest = json.loads(manifest_file.read_text())
    manifest['packs'] = [{'name': 'scenes', 'type': 'Scene', 'path': 'packs/scenes'}]
    manifest_file.write_text(json.dumps(manifest))
    (level / 'packs/scenes.db').unlink()  # Only the newly copied synthetic fixture.
    with plyvel_next.DB(str(level / 'packs/scenes'), create_if_missing=True) as db:
        db.put(b'!scenes!scene-crypt', json.dumps(scene).encode())
    level_report = run(cli, 'convert', level, '--out', out / 'leveldb-output')
    assert level_report['status'] == 'PASS'
    gui_report = out / 'gui-check.json'
    run(gui, '--bundle-check', gui_report, as_json=False)
    gui_result = json.loads(gui_report.read_text())
    assert gui_result['status'] == 'PASS' and gui_result['version'] == version.split(' ', 1)[1]
    installation = {'status': 'SKIPPED (local Toolkit running; guard not bypassed)'}
    if not skip_install:
        assets = out / 'fake/MyAssets'; assets.mkdir(parents=True)
        original = assets / 'user.txt'; original.write_bytes(b'original user file')
        before = hashlib.sha256(original.read_bytes()).hexdigest()
        installation = run(cli, 'install', '--package', native_zip, '--myassets', assets, '--backup-root', out / 'backups')
        receipt = json.loads(Path(installation['receipt']).read_text())
        note = next(r for r in receipt['added'] if r['path'].endswith('.rwnote'))
        kept = assets.parent / note['path']
        with kept.open('ab') as stream: stream.write(b'\nsynthetic preserved user edit')
        removed = run(cli, 'install', '--uninstall', installation['receipt'], '--keep-changed')
        assert removed['removed'] == installation['added'] - 1
        assert removed['kept_changed'] == [note['path']]
        assert hashlib.sha256(original.read_bytes()).hexdigest() == before and kept.is_file()
        assert {p for p in assets.rglob('*') if p.is_file()} == {original, kept}
        installation['uninstall'] = removed
    report = {'status': 'PASS' if not skip_install else 'PARTIAL (local install skipped)',
              'version': version, 'python_on_exe_path': False, 'fixture_pdf_mode': plain['pdf_mode'],
              'rendered_pdf_pages': 2, 'leveldb_native_conversion': level_report['status'],
              'gui': gui_result, 'installation': installation, 'commands': commands}
    (out / 'smoke-summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', required=True)
    parser.add_argument('--fixture', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--skip-install', action='store_true', help='Local diagnostic only; CI must run all phases')
    args = parser.parse_args()
    print(json.dumps(smoke(args.zip, args.fixture, args.out, skip_install=args.skip_install), indent=2))
