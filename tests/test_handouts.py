import json
import io
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from forgebridge.handouts import main, media_references, write_handouts_zip


def companion(refs):
    return {'scene_id': 'crypt', 'scene_notes': {'dependencies': {'documents': [
        {'document_type': 'JournalEntry', 'payload': {'name': 'Rooms', 'pages': [
            {'name': str(i), 'src': ref} for i, ref in enumerate(refs)]}}]}}}


class HandoutTests(unittest.TestCase):
    def write(self, tmp, refs, assets, *, zipped=False):
        root = Path(tmp)
        package = root / ('package.zip' if zipped else 'package')
        if zipped:
            with zipfile.ZipFile(package, 'w') as z:
                z.writestr('content/module.json', '{"id":"sample"}')
                for name, data in assets.items():
                    z.writestr('content/' + name, data)
        else:
            package.mkdir()
            (package / 'module.json').write_text('{"id":"sample"}')
            for name, data in assets.items():
                path = package / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        source = root / 'source.json'
        source.write_text(json.dumps(companion(refs)))
        dest = root / 'handouts.zip'
        report = write_handouts_zip(package, source, dest)
        return package, source, dest, report

    def test_zip_namespaces_url_encoding_and_basename_collisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, dest, report = self.write(tmp, ['modules/sample/a/Room%20One.png',
                'a/Room One.png', 'modules/sample/b/Room One.png', 'missing.pdf'],
                {'a/Room One.png': b'first', 'b/Room One.png': b'second'}, zipped=True)
            self.assertEqual(report['copied_files'], 2)
            self.assertEqual(report['counts'], {'copied': 3, 'missing': 1})
            copied = [r for r in report['references'] if r['status'] == 'copied']
            self.assertEqual(len({r['bundled_path'] for r in copied}), 2)
            with zipfile.ZipFile(dest) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual({z.read(r['bundled_path']) for r in copied}, {b'first', b'second'})
                self.assertEqual(json.loads(z.read('handout-report.json')), report)
                self.assertFalse(any(n.startswith('MyAssets/') for n in z.namelist()))

    def test_local_only_no_traversal_and_no_unsupported_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, report = self.write(tmp, ['https://example.com/x.png', '//example.com/x.pdf',
                '../secret.png', '%2e%2e/secret.png', 'C:/secret.png', '/secret.png',
                'modules/other/a.png', 'macro.js', 'a.png'], {'a.png': b'one'})
            self.assertEqual(report['counts'], {'external_reference': 2, 'rejected_path': 4,
                'other_package_reference': 1, 'unsupported_type': 1, 'copied': 1})

    def test_html_media_scan_and_active_content_ignored(self):
        x = companion(['page.pdf'])
        payload = x['scene_notes']['dependencies']['documents'][0]['payload']
        payload['pages'][0]['text'] = {'content': '<p><img src="one.png"><a href="two.pdf">PDF</a>'
            '<a href="https://example.com">site</a><video poster="poster.jpg"><source src="clip.webm"></video>'
            '<script><img src="bad.png"></script><iframe src="bad.pdf"></iframe></p>'}
        payload['pages'].append({'text': {'format': 2, 'content': '<img src="plain.png">'}})
        refs = media_references(x)
        self.assertEqual(set(refs), {'page.pdf', 'one.png', 'two.pdf', 'poster.jpg', 'clip.webm'})
        self.assertEqual(refs['one.png'][0]['path'], 'pages[0].text.content')

    def test_symlinks_are_not_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            package, source, _, _ = self.write(tmp, [], {})
            secret = Path(tmp) / 'secret.png'
            secret.write_bytes(b'secret')
            try:
                (package / 'link.png').symlink_to(secret)
            except OSError as exc:
                if getattr(exc, "winerror", None) != 1314:
                    raise
                self.skipTest("Windows symlink creation privilege unavailable (WinError 1314)")
            source.write_text(json.dumps(companion(['link.png'])))
            report = write_handouts_zip(package, source, Path(tmp) / 'second.zip')
            self.assertEqual(report['counts'], {'missing_or_unsafe': 1})

    def test_size_limit_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            package, source, dest, _ = self.write(tmp, ['a.png'], {'a.png': b'12345'})
            before = dest.read_bytes()
            with self.assertRaises(ValueError):
                write_handouts_zip(package, source, dest)
            self.assertEqual(dest.read_bytes(), before)
            with patch('forgebridge.handouts.MAX_FILE', source.stat().st_size), patch('forgebridge.handouts.MAX_TOTAL', 4):
                with self.assertRaisesRegex(ValueError, '256 MiB'):
                    write_handouts_zip(package, source, Path(tmp) / 'overflow.zip')
            self.assertFalse((Path(tmp) / 'overflow.zip').exists())

    def test_duplicate_normalized_zip_paths_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            package, source, _, _ = self.write(tmp, [], {}, zipped=True)
            with zipfile.ZipFile(package, 'a') as z:
                z.writestr('content/a.png', b'one')
                z.writestr('content/./a.png', b'two')
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                write_handouts_zip(package, source, Path(tmp) / 'second.zip')

    def test_cli_success_and_missing_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            package, source, _, _ = self.write(tmp, ['a.png'], {'a.png': b'one'})
            dest = Path(tmp) / 'cli.zip'
            args = ['--package', str(package), '--companion', str(source), '--out', str(dest)]
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(main(args), 0)
            self.assertIn('Collected 1 media files', out.getvalue())
            args[1] = str(Path(tmp) / 'missing.zip')
            args[-1] = str(Path(tmp) / 'missing-output.zip')
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main(args), 1)
            self.assertFalse(Path(args[-1]).exists())


if __name__ == '__main__':
    unittest.main()
