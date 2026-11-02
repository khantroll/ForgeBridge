import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from PIL import Image
from forgebridge.handouts import write_handouts_zip
from forgebridge.native_images import write_source_images_zip
from forgebridge.nrbf import Reader
from forgebridge.pdf_pages import render_pdf_pages
from test_native_images import inputs


def pdf_fixture(count=2):
    # Inert two-colour pages; no PDF authoring dependency needed by tests.
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>',
               ('<< /Type /Pages /Count %d /Kids [%s] >>' %
                (count, ' '.join(f'{3+2*i} 0 R' for i in range(count)))).encode()]
    for i in range(count):
        w, h = (200, 100) if i % 2 == 0 else (100, 200)
        content = ('1 0 0' if i % 2 == 0 else '0 0 1') + f' rg 0 0 {w} {h} re f'
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w} {h}] /Resources << >> /Contents {4+2*i} 0 R >>'.encode())
        objects.append(f'<< /Length {len(content)} >>\nstream\n{content}\nendstream'.encode())
    data, offsets = b'%PDF-1.4\n', [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(data));data += f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n'
    start = len(data)
    data += f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode()
    data += b''.join(f'{offset:010} 00000 n \n'.encode() for offset in offsets[1:])
    return data + f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode()


@unittest.skipUnless(importlib.util.find_spec('pypdfium2'), 'optional PDF renderer not installed')
class PdfPageTests(unittest.TestCase):
    def test_render_page_order_and_proportions(self):
        pages = render_pdf_pages(pdf_fixture())
        self.assertEqual(len(pages), 2)
        for png, size, colour in zip(pages, [(400, 200), (200, 400)], [(255, 0, 0), (0, 0, 255)]):
            with Image.open(io.BytesIO(png)) as image:
                self.assertEqual(image.size, size)
                self.assertEqual(image.convert('RGB').getpixel((20, 20)), colour)

    def test_invalid_and_oversized_pdf(self):
        with self.assertRaisesRegex(ValueError, 'cannot be opened'):
            render_pdf_pages(b'not a PDF')
        with self.assertRaisesRegex(ValueError, 'page count'):
            render_pdf_pages(pdf_fixture(33))
        with patch('forgebridge.pdf_pages.MAX_RENDERED_BYTES', 1):
            with self.assertRaisesRegex(ValueError, '64 MiB'):
                render_pdf_pages(pdf_fixture())

    def test_native_page_attachments_original_pdf_and_default_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            template, companion, bundle, x = inputs(tmp)
            original = pdf_fixture()
            (Path(tmp) / 'package/private/file.pdf').write_bytes(original)
            bundle.unlink();write_handouts_zip(Path(tmp) / 'package', companion, bundle)
            disabled = write_source_images_zip(companion, bundle, template, Path(tmp) / 'off.zip')
            self.assertEqual(disabled['counts']['native_pdf_pages'], 0)
            dest = Path(tmp) / 'on.zip'
            report = write_source_images_zip(companion, bundle, template, dest, pdf_pages=True)
            self.assertEqual(report['native_folder'], disabled['native_folder'])
            self.assertEqual(report['placements'], disabled['placements'])
            self.assertEqual(report['counts']['native_pdf_documents'], 1)
            self.assertEqual(report['counts']['native_pdf_pages'], 2)
            row = next(r for r in report['source_media'] if r['status'] == 'native_pdf_pages')
            attachments = [a for a in report['attached_media'] if a['ref'] == row['ref']]
            self.assertEqual([a['label'] for a in attachments], ['PDF — file — Page 1 of 2', 'PDF — file — Page 2 of 2'])
            with zipfile.ZipFile(dest) as z:
                self.assertEqual(z.read(row['original_pdf']), original)
                self.assertFalse(row['original_pdf'].startswith('MyAssets/'))
                for i, page in enumerate(row['pages']):
                    reader = Reader(z.read(page['target'][:-7] + '.rwfile'));reader.read()
                    png = next(o['bytes'] for o in reader.objects.values() if isinstance(o, dict) and 'bytes' in o)
                    with Image.open(io.BytesIO(png)) as image:
                        self.assertEqual(image.convert('RGB').getpixel((20, 20)), [(255, 0, 0), (0, 0, 255)][i])
            # Corrupt PDFs remain explicit references, not partial native pages.
            (Path(tmp) / 'package/private/file.pdf').write_bytes(b'bad')
            bundle.unlink();write_handouts_zip(Path(tmp) / 'package', companion, bundle)
            failed = write_source_images_zip(companion, bundle, template, Path(tmp) / 'failed.zip', pdf_pages=True)
            self.assertEqual(failed['counts']['native_pdf_pages'], 0)
            self.assertTrue(any(r['status'] == 'pdf_reference_only' for r in failed['source_media']))
