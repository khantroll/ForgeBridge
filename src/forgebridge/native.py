"""Experimental native notes; synthetic text, links and tables passed import tests.

This emits only known note classes from the user's exported sample. It does
not create maps, load CLR types, or convert source permissions automatically.
"""
from collections import deque
from dataclasses import dataclass
import argparse
import json
from pathlib import Path
from pathlib import PurePosixPath
import struct
import zipfile

from forgebridge.nrbf import inspect_nrbf


@dataclass(eq=False)
class Node:
    schema: dict
    members: dict
    inline: bool = False


@dataclass(eq=False)
class Array:
    items: list
    kind: int
    info: object = None


class NoteBuilder:
    def __init__(self):
        self.schema = json.loads(Path(__file__).with_name('arkenforge-note-schema.json').read_text())

    def definition(self, name):
        matches = [m for m in self.schema['classes'] if m['name'] == name or m['name'].startswith(name + '`1[')]
        if len(matches) != 1:
            raise ValueError(f'Unknown or ambiguous native schema: {name}')
        return matches[0]

    def node(self, name, members, *, inline=False):
        schema = self.definition(name)
        if set(members) != set(schema['names']):
            raise ValueError(f'Member mismatch: {name}')
        return Node(schema, members, inline)

    def vector(self, x, y, z):
        return self.node('SVector3', dict(x=x, y=y, z=z))

    def sequence(self, name, items):
        schema = self.definition(name)
        kind, info = schema['types'][0], schema['infos'][0]
        # _items can be StringArray or a named Class array.
        array = Array(list(items), 1 if kind == 6 else 4, None if kind == 6 else {'name': info['name'][:-2], 'library_id': info['library_id']})
        return Node(schema, {'_items': array, '_size': len(items), '_version': len(items)})

    def strings(self, values=()):
        return self.sequence('System.Collections.Generic.List`1[[System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089]]', list(values))

    def icon(self):
        return self.node('ArkenNoteIcon', {'_iconPath': 'MARKER|Markers/NoteMarker', '_hue': .5, '_sat': .5, '_bri': .5, '_opa': 1., '_tint': None})

    def text(self, segments):
        chars = []
        if sum(len(text) for text, link in segments) > 64000:
            raise ValueError('Native text exceeds experimental limit')
        for text, link in segments:
            if link is not None and (not link.startswith('MyAssets/Encyclopedia/Notes/') or
                    '..' in PurePosixPath(link).parts or '\\' in link or not link.endswith('.rwmeta')):
                raise ValueError('Link is outside the generated notes')
            for char in text:
                if ord(char) > 65535 or 0xD800 <= ord(char) <= 0xDFFF:
                    raise ValueError('Non-BMP native characters are not yet supported')
                settings = self.node('ArkenTextCharacter+FontSettings', {'value__': 1024 if link else 0}, inline=True)
                chars.append(self.node('ArkenTextCharacter', {'_character': char, '_size': 40, '_alignment': 0,
                    '_fontSettings': settings, '_hexColour': 'B9CEFF' if link else '', '_link': link,
                    '_defaultFont': 'ToolkitDefault', '_isUnicode': False, '_unicodeCharacter': '\0'}))
        return self.node('ArkenTextString', {'_characters': self.sequence('System.Collections.Generic.List`1[[ArkenTextCharacter, Unity.TextMeshPro, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]', chars), '_font': 'ToolkitDefault'})

    def field_members(self, name, uid):
        visible = self.strings()
        return {'_name': name, '_visibleToPlayers': visible, '_UID': uid,
                'ArkenNoteField+_name': name, 'ArkenNoteField+_visibleToPlayers': visible, 'ArkenNoteField+_UID': uid}

    def text_field(self, name, segments, uid):
        return self.node('ArkenNoteFieldText', {**self.field_members(name, uid), '_text': self.text(segments),
            '_fieldColor': self.vector(.15, .15, .15), '_headingColor': self.vector(1., 1., 1.),
            '_bgOpacity': 1., '_showBorder': False, '_font': 'ToolkitDefault'})

    def media_field(self, name, target, uid):
        if (not isinstance(target, str) or not target.startswith('MyAssets/Media/') or
                '\\' in target or '..' in PurePosixPath(target).parts or not target.endswith('.rwmeta')):
            raise ValueError('Media target must be native metadata inside MyAssets/Media')
        return self.node('ArkenNoteFieldMedia', {**self.field_members(name, uid),
            '_contentPathRelative': target, '_frameColor': self.vector(.15, .15, .15),
            '_headingColor': self.vector(1., 1., 1.), '_showBorder': True, '_customScale': 1.})

    def table_field(self, name, rows, uid):
        if not rows or len(rows) > 256:
            raise ValueError('Table must have 1 to 256 rows')
        built, covered = [], set()
        for start, end, text in rows:
            if type(start) is not int or type(end) is not int or not 1 <= start <= end <= 1000000:
                raise ValueError('Invalid native table range')
            if any(start <= b and end >= a for a, b in covered):
                raise ValueError('Overlapping native table ranges')
            covered.add((start, end))
            segments = [(text, None)] if isinstance(text, str) else text
            built.append(self.node('ArkenNoteFieldRollableTableRow', {'_from': start, '_to': end, '_data': self.text(segments)}))
        return self.node('ArkenNoteFieldRollableTable', {**self.field_members(name, uid),
            '_rows': self.sequence('System.Collections.Generic.List`1[[ArkenNoteFieldRollableTableRow, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]', built)})

    def note(self, name, fields, *, tag='ForgeBridge smoke test'):
        entries = [self.node('KVPOrderedList`1+KVPEntry', {'_order': i, '_value': f}) for i, f in enumerate(fields)]
        ordered = self.node('KVPOrderedList', {'_entries': self.sequence('System.Collections.Generic.List`1[[KVPOrderedList`1+KVPEntry`1[[ArkenNoteField, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null],[ArkenNoteField, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]], Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]', entries)})
        category = self.node('ArkenNoteFieldCategory', {**self.field_members('', 0), '_content': ordered,
            '_color': self.vector(.15, .15, .15), '_open': True})
        return self.node('ArkenNoteUpgrade', {'_name': name, '_pack': '', '_creator': 'ForgeBridge', '_aliases': self.strings(),
            '_tags': self.strings([tag]), '_tooltipSummary': '', '_noteIcon': self.icon(),
            '_bgColour': self.vector(.15, .15, .15), '_locked': False, '_linkColourFix': True, '_noteIconFieldFix': True,
            '_indicatedStats': self.sequence('System.Collections.Generic.List`1[[ArkenNoteFieldStat, Assembly-CSharp, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null]]', []),
            '_noteFields': category, '_bgImage': None, '_bgImageTiled': False, 'nextUID': len(fields) + 1})

    def metadata(self, name):
        schema = self.definition('ArkenNoteUpgradeMeta')
        members = {}
        for field, kind in zip(schema['names'], schema['types']):
            bare = field.split('+')[-1]
            if bare == '_name': value = name
            elif bare == '_noteIcon': value = self.icon()
            elif bare in ('_aliases', '_tags', '_links'): value = self.strings()
            elif bare in ('_includedWorldPaths', '_prevPathIfDeleted'): value = None
            elif kind == 0: value = False
            else: value = ''
            members[field] = value
        # Preserve identity of repeated inherited lists and name values.
        for field in members:
            bare = field.split('+')[-1]
            if '+' in field and bare in members: members[field] = members[bare]
        return Node(schema, members)


class Writer:
    """Emit this known note object graph as NRBF, without a deserializer."""
    def __init__(self, libraries):
        self.libraries = libraries
        self.out = bytearray()
        self.ids, self.string_ids, self.metadata_ids = {}, {}, {}
        self.next_id = 3
        self.queue = deque()
        self.records = 0

    def integer(self, value):
        self.out += struct.pack('<i', value)

    def string(self, value):
        data = value.encode('utf-8'); size = len(data)
        while size >= 128:
            self.out.append((size & 127) | 128); size >>= 7
        self.out.append(size); self.out += data

    def allocate(self, value):
        key = id(value)
        if key not in self.ids:
            self.ids[key] = self.next_id; self.next_id += 1
            self.queue.append(value)
        return self.ids[key]

    def primitive(self, kind, value):
        if kind == 3:
            if not isinstance(value, str) or len(value) != 1 or ord(value) > 65535:
                raise ValueError('Invalid Char')
            self.out += value.encode('utf-8')
        else:
            formats = {1: '?', 2: 'B', 6: 'd', 7: 'h', 8: 'i', 9: 'q', 10: 'b', 11: 'f'}
            if kind not in formats: raise ValueError('Unsupported writer primitive')
            self.out += struct.pack('<' + formats[kind], value)

    def type_info(self, kind, info):
        if kind == 0: self.out.append(info)
        elif kind == 3: self.string(info)
        elif kind == 4: self.string(info['name']); self.integer(info['library_id'])
        elif kind == 7: self.out.append(info)  # primitive array element type
        elif kind not in (1, 2, 5, 6): raise ValueError('Unsupported writer type')

    def value(self, value):
        if value is None: self.out.append(10)
        elif isinstance(value, str):
            if value in self.string_ids:
                self.out.append(9); self.integer(self.string_ids[value])
            else:
                oid = self.next_id; self.next_id += 1; self.string_ids[value] = oid
                self.out.append(6); self.integer(oid); self.string(value)
        elif isinstance(value, Node) and value.inline:
            oid = -self.next_id; self.next_id += 1
            self.node(value, oid)
        elif isinstance(value, (Node, Array)):
            self.out.append(9); self.integer(self.allocate(value))
        else: raise ValueError('Unsupported writer value')

    def node(self, node, oid):
        m = node.schema
        key = json.dumps(m, sort_keys=True)
        if key in self.metadata_ids:
            self.out.append(1); self.integer(oid); self.integer(self.metadata_ids[key])
        else:
            self.metadata_ids[key] = oid
            self.out.append(4 if m['library_id'] is None else 5)
            self.integer(oid); self.string(m['name']); self.integer(len(m['names']))
            for name in m['names']: self.string(name)
            self.out += bytes(m['types'])
            for kind, info in zip(m['types'], m['infos']): self.type_info(kind, info)
            if m['library_id'] is not None: self.integer(m['library_id'])
        for name, kind, info in zip(m['names'], m['types'], m['infos']):
            if kind == 0: self.primitive(info, node.members[name])
            else: self.value(node.members[name])

    def array(self, array, oid):
        self.out.append(7); self.integer(oid); self.out.append(0); self.integer(1); self.integer(len(array.items))
        self.out.append(array.kind); self.type_info(array.kind, array.info)
        for item in array.items: self.value(item)

    def write(self, root):
        self.ids[id(root)] = 1; self.queue.append(root)
        self.out.append(0)
        for v in (1, -1, 1, 0): self.integer(v)
        for lid, name in self.libraries.items():
            self.out.append(12); self.integer(int(lid)); self.string(name)
        while self.queue:
            value = self.queue.popleft(); oid = self.ids[id(value)]
            self.records += 1
            if self.records > 200000 or len(self.out) > 64 * 1024 * 1024: raise ValueError('Native output exceeds limit')
            if isinstance(value, Node): self.node(value, oid)
            else: self.array(value, oid)
        self.out.append(11)
        data = bytes(self.out)
        inspect_nrbf(data)  # Structure check only; does not prove Arkenforge compatibility.
        return data


def smoke_files():
    builder = NoteBuilder()
    base = 'MyAssets/Encyclopedia/Notes/ForgeBridgeTests/'
    names = ['ForgeBridge Native Test A', 'ForgeBridge Native Test B']
    paths = [base + name for name in names]
    files = {}
    for index, name in enumerate(names):
        other = 1 - index
        segments = [('ForgeBridge generated this text. Open ', None), (names[other], paths[other] + '.rwmeta'), ('.\nThe next line should remain visible.\nSecond line: 12345.', None)]
        fields = [builder.text_field('Generated text and link', segments, 1)]
        if index == 0:
            fields.append(builder.table_field('Generated 1-3 test table', [(1, 1, 'ForgeBridge result one'), (2, 2, 'ForgeBridge result two'), (3, 3, 'ForgeBridge result three')], 2))
        files[paths[index] + '.rwnote'] = Writer(builder.schema['libraries']).write(builder.note(name, fields))
        files[paths[index] + '.rwmeta'] = Writer(builder.schema['libraries']).write(builder.metadata(name))
    return files


def write_smoke_zip(dest):
    dest = Path(dest)
    if dest.exists() or dest.is_symlink(): raise ValueError('Choose a new output filename')
    dest.parent.mkdir(parents=True, exist_ok=True)
    files = smoke_files()
    with zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in files.items(): archive.writestr(path, data)
    return len(files)


def main():
    parser = argparse.ArgumentParser(description='Generate experimental native Arkenforge note smoke-test files')
    parser.add_argument('--out', required=True, help='New ZIP output path')
    parser.add_argument('--companion', help='Existing .forgebridge.json to convert instead of generating a smoke test')
    args = parser.parse_args()
    try:
        if args.companion:
            from forgebridge.native_export import write_companion_zip
            report = write_companion_zip(args.companion, args.out)
            print(f"Wrote {report['counts']['notes']} native notes; see INSTALL.txt and conversion-report.json in ZIP. Real source import requires verification.")
            return
        count = write_smoke_zip(args.out)
    except (ValueError, OSError) as exc: parser.exit(1, str(exc) + '\n')
    print(f'Wrote {count} native test files. Arkenforge import remains unverified.')


if __name__ == '__main__': main()
