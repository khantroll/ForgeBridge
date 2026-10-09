"""Collect retained journal media for inspection, without creating native assets."""
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import stat
import sys
from urllib.parse import unquote, urlsplit
import zipfile

from forgebridge.inventory import _safe_zip_name
from forgebridge.uvtt import _package_file
from forgebridge.validate import InventoryFatal

EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.pdf', '.mp3', '.ogg',
              '.wav', '.mp4', '.m4v', '.webm'}
MAX_FILE = 64 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024


class MediaParser(HTMLParser):
    def __init__(self, add):
        super().__init__(convert_charrefs=True)
        self.add = add
        self.suppressed = []

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style', 'iframe', 'object'}:
            self.suppressed.append(tag)
        if self.suppressed:
            return
        attrs = dict(attrs)
        for field in ('src', 'poster') if tag in {'img', 'audio', 'video', 'source'} else ():
            if attrs.get(field):
                self.add(attrs[field])
        if tag == 'a' and attrs.get('href'):
            ref = attrs['href']
            if Path(unquote(urlsplit(ref).path)).suffix.lower() in EXTENSIONS:
                self.add(ref)

    def handle_endtag(self, tag):
        if self.suppressed and self.suppressed[-1] == tag:
            self.suppressed.pop()


def media_references(companion, *, occurrence_order=None):
    documents = companion.get('scene_notes', {}).get('dependencies', {}).get('documents')
    if not isinstance(documents, list) or len(documents) > 256:
        raise ValueError('Companion needs a bounded retained dependency graph')
    refs = {}

    def scan(value, origin, *, html=False):
        def add(ref):
            if not isinstance(ref, str) or not ref:
                return
            if len(ref) > 8192:
                raise ValueError('Media reference exceeds length limit')
            refs.setdefault(ref, []).append(origin)
            if occurrence_order is not None:
                occurrence_order.append((ref, origin))
            if sum(len(x) for x in refs.values()) > 4096:
                raise ValueError('Too many media references')
        if isinstance(value, str):
            if html:
                parser = MediaParser(add)
                parser.feed(value)
                parser.close()
            else:
                add(value)

    for di, document in enumerate(documents):
        if not isinstance(document, dict) or not isinstance(document.get('payload'), dict):
            raise ValueError('Invalid retained document')
        payload = document['payload']
        def field(value, path, html=False):
            scan(value, {'document_index': di, 'document_name': payload.get('name'), 'path': path}, html=html)
        field(payload.get('img'), 'img')
        if document.get('document_type') == 'JournalEntry':
            field(payload.get('content'), 'content', True)
            pages = payload.get('pages', [])
            if not isinstance(pages, list) or len(pages) > 512:
                raise ValueError('Invalid journal pages')
            for pi, page in enumerate(pages):
                if not isinstance(page, dict):
                    raise ValueError('Invalid journal page')
                field(page.get('src'), f'pages[{pi}].src')
                text = page.get('text')
                if isinstance(text, dict) and text.get('format') != 2:
                    field(text.get('content'), f'pages[{pi}].text.content', True)
        elif document.get('document_type') == 'RollTable':
            field(payload.get('description'), 'description', True)
            results = payload.get('results', [])
            if not isinstance(results, list) or len(results) > 256:
                raise ValueError('Invalid table results')
            for ri, result in enumerate(results):
                if not isinstance(result, dict):
                    raise ValueError('Invalid table result')
                field(result.get('img'), f'results[{ri}].img')
                field(result.get('description', result.get('text')), f'results[{ri}].text', True)
    return refs


class PackageMedia:
    def __init__(self, path):
        self.path = Path(path)
        self.archive, self.entries = None, {}
        self.prefix = ''
        try:
            if self.path.is_dir():
                manifests = [self.path / name for name in ('module.json', 'world.json', 'system.json') if (self.path / name).is_file()]
                if len(manifests) != 1:
                    raise ValueError('Package directory needs exactly one manifest')
                manifest = _package_file(self.path, manifests[0].name)
                if manifest.stat().st_size > 1024 * 1024:
                    raise ValueError('Manifest exceeds size limit')
                payload = json.loads(manifest.read_text(encoding='utf-8'))
            else:
                self.archive = zipfile.ZipFile(self.path)
                if len(self.archive.infolist()) > 50000:
                    raise ValueError('Package has too many entries')
                for entry in self.archive.infolist():
                    safe, problem = _safe_zip_name(entry.filename)
                    if problem or entry.is_dir() or stat.S_ISLNK(entry.external_attr >> 16):
                        continue
                    if safe in self.entries:
                        raise ValueError('Duplicate normalized package path')
                    self.entries[safe] = entry
                manifests = [name for name in self.entries if name.count('/') <= 1 and Path(name).name in {'module.json', 'world.json', 'system.json'}]
                if len(manifests) != 1:
                    raise ValueError('Package ZIP needs exactly one root or single-folder manifest')
                entry = self.entries[manifests[0]]
                if entry.file_size > 1024 * 1024:
                    raise ValueError('Manifest exceeds size limit')
                payload = json.loads(self.archive.read(entry))
                self.prefix = manifests[0][:-len(Path(manifests[0]).name)]
            self.package_id = payload.get('id') or payload.get('name')
            if not isinstance(self.package_id, str) or not self.package_id:
                raise ValueError('Manifest needs a package id')
        except Exception:
            self.close()
            raise

    def close(self):
        if self.archive:
            self.archive.close()

    def read(self, ref):
        if re.match(r'^[A-Za-z]:[/\\]', ref):
            return {'status': 'rejected_path'}, None
        parts = urlsplit(ref)
        if parts.scheme or parts.netloc:
            return {'status': 'external_reference'}, None
        safe, problem = _safe_zip_name(unquote(parts.path))
        if problem:
            return {'status': 'rejected_path'}, None
        bits = safe.split('/')
        if bits[0] in {'modules', 'worlds', 'systems'}:
            if len(bits) < 3 or bits[1] != self.package_id:
                return {'status': 'other_package_reference'}, None
            safe = '/'.join(bits[2:])
        if Path(safe).suffix.lower() not in EXTENSIONS:
            return {'status': 'unsupported_type'}, None
        if self.archive:
            entry = self.entries.get(self.prefix + safe)
            if not entry:
                return {'status': 'missing'}, None
            size = entry.file_size
            if size > MAX_FILE:
                return {'status': 'too_large'}, None
            data = self.archive.read(entry)
        else:
            try:
                path = _package_file(self.path, safe)
            except InventoryFatal:
                return {'status': 'missing_or_unsafe'}, None
            size = path.stat().st_size
            if size > MAX_FILE:
                return {'status': 'too_large'}, None
            with path.open('rb') as stream:
                data = stream.read(MAX_FILE + 1)
            if len(data) > MAX_FILE:
                return {'status': 'too_large'}, None
        return {'status': 'copied', 'package_path': safe, 'size': len(data),
                'sha256': hashlib.sha256(data).hexdigest()}, data


def write_handouts_zip(package, companion_path, dest):
    companion_path, dest = Path(companion_path), Path(dest)
    if companion_path.stat().st_size > MAX_FILE:
        raise ValueError('Companion exceeds size limit')
    if dest.exists() or dest.is_symlink():
        raise ValueError('Choose a new output filename')
    companion = json.loads(companion_path.read_text(encoding='utf-8'))
    refs = media_references(companion)
    files, rows, paths, total = {}, [], {}, 0
    media = PackageMedia(package)
    try:
        for ref, origins in sorted(refs.items()):
            details, data = media.read(ref)
            row = {'ref': ref, 'origins': origins, **details}
            if data is not None:
                source = details['package_path']
                if source not in paths:
                    total += len(data)
                    if total > MAX_TOTAL:
                        raise ValueError('Collected media exceeds 256 MiB limit')
                    basename = re.sub(r'[^A-Za-z0-9._-]', '_', Path(source).stem)[:120] + Path(source).suffix.lower()
                    target = 'assets/' + hashlib.sha256(source.encode()).hexdigest()[:16] + '-' + basename
                    paths[source] = target
                    files[target] = data
                row['bundled_path'] = paths[source]
            rows.append(row)
    finally:
        media.close()
    report = {'schema_version': '1.0', 'scene_id': companion.get('scene_id'),
              'package_id': media.package_id, 'references': rows,
              'counts': dict(Counter(row['status'] for row in rows)),
              'copied_files': len(files), 'copied_bytes': total,
              'native_links_rewritten': False}
    files['handout-report.json'] = json.dumps(report, indent=2, ensure_ascii=True).encode()
    files['README.txt'] = ("ForgeBridge journal media collection\n\n"
        "These are original source files, not native Arkenforge assets.\n"
        "Extract to a separate folder; do not copy this bundle into MyAssets.\n"
        "handout-report.json maps journal references to collected files and reports gaps.\n"
        "Open an image/PDF to verify it matches the linked journal page.\n"
        "Existing Arkenforge note links are unchanged. Native media linking needs a separate test.\n"
        "Private source content: do not publish this bundle.\n").encode()
    dest.parent.mkdir(parents=True, exist_ok=True)
    created = False
    try:
        with dest.open('xb') as stream:
            created = True
            with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                for name, data in files.items():
                    archive.writestr(name, data)
    except Exception:
        # Do not leave a partial collection presented as a finished bundle.
        if created and dest.exists():
            dest.unlink()
        raise
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, help='Original Foundry ZIP or package directory')
    parser.add_argument('--companion', required=True, help='Retained scene .forgebridge.json')
    parser.add_argument('--out', required=True, help='New ZIP filename')
    args = parser.parse_args(argv)
    try:
        report = write_handouts_zip(args.package, args.companion, args.out)
    except (OSError, ValueError, InventoryFatal, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Collected {report['copied_files']} media files. Reference statuses: {report['counts']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
