"""Read a bounded subset of MS-NRBF into inert records for format research.

No CLR types are loaded or instantiated. References remain explicit IDs, so
cycles are not expanded. This is an inspector, not an Arkenforge serializer.
"""
import math
import struct


class NrbfError(ValueError):
    pass


class Reader:
    def __init__(self, data, *, max_bytes=64 * 1024 * 1024,
                 max_records=200000, max_items=2000000, max_depth=128):
        if len(data) > max_bytes:
            raise NrbfError('Input exceeds byte limit')
        self.data, self.pos = memoryview(data), 0
        self.max_records, self.max_items, self.max_depth = max_records, max_items, max_depth
        self.record_count, self.item_count = 0, 0
        self.objects, self.classes, self.libraries = {}, {}, {}
        self.depth = 0

    def take(self, count):
        if count < 0 or self.pos + count > len(self.data):
            raise NrbfError(f'Truncated record at byte {self.pos}')
        value = self.data[self.pos:self.pos + count]
        self.pos += count
        return value

    def number(self, fmt):
        return struct.unpack('<' + fmt, self.take(struct.calcsize('<' + fmt)))[0]

    def byte(self):
        return self.number('B')

    def integer(self):
        return self.number('i')

    def count(self, count):
        if count < 0 or self.item_count + count > self.max_items:
            raise NrbfError('Invalid count or item limit exceeded')
        self.item_count += count
        return count

    def string(self):
        size = 0
        for shift in range(0, 35, 7):
            part = self.byte()
            if shift == 28 and part > 15:
                raise NrbfError('Invalid string length')
            size |= (part & 127) << shift
            if not part & 128:
                try:
                    return bytes(self.take(size)).decode('utf-8')
                except UnicodeDecodeError as exc:
                    raise NrbfError('Invalid UTF-8 string') from exc
        raise NrbfError('Invalid string length')

    def primitive(self, kind):
        formats = {1: 'B', 2: 'B', 6: 'd', 7: 'h', 8: 'i', 9: 'q',
                   10: 'b', 11: 'f', 12: 'q', 13: 'Q', 14: 'H', 15: 'I', 16: 'Q'}
        if kind == 3:  # BinaryReader Char is a UTF-8 character.
            first = self.byte()
            length = 1 if first < 128 else 2 if 194 <= first <= 223 else 3 if 224 <= first <= 239 else 0
            if not length:
                raise NrbfError('Unsupported or invalid Char')
            try:
                return (bytes([first]) + bytes(self.take(length - 1))).decode('utf-8')
            except UnicodeDecodeError as exc:
                raise NrbfError('Invalid Char') from exc
        if kind in (5, 18):
            return self.string()  # Decimal stays a string; no evaluation.
        if kind == 17:
            return None
        if kind not in formats:
            raise NrbfError(f'Unsupported primitive {kind}')
        value = self.number(formats[kind])
        if kind == 1:
            if value not in (0, 1):
                raise NrbfError('Invalid Boolean')
            return bool(value)
        return value

    def type_info(self, kind):
        if kind in (0, 7):
            return self.byte()
        if kind == 3:
            return self.string()
        if kind == 4:
            return {'name': self.string(), 'library_id': self.integer()}
        if kind not in (1, 2, 5, 6):
            raise NrbfError(f'Unsupported binary type {kind}')
        return None

    def put(self, oid, value):
        if oid == 0 or oid in self.objects:
            raise NrbfError('Invalid or duplicate object ID')
        self.objects[oid] = value
        return {'ref': oid}

    def value(self):
        while True:
            value = self.record()
            if value != {'library_record': True}:
                return value

    def members(self, oid, metadata):
        obj = {'class': metadata['name'], 'library_id': metadata['library_id'], 'members': {}}
        ref = self.put(oid, obj)
        for name, kind, info in zip(metadata['names'], metadata['types'], metadata['infos']):
            value = self.primitive(info) if kind == 0 else self.value()
            if isinstance(value, dict) and ('nulls' in value or 'end' in value):
                raise NrbfError('Unexpected array null run or message end in class')
            obj['members'][name] = value
        return ref

    def array(self, oid, lengths, kind, info, bounds=None):
        size = self.count(math.prod(lengths))
        obj = {'array_type': kind, 'lengths': lengths, 'lower_bounds': bounds, 'items': []}
        ref = self.put(oid, obj)
        if kind == 0 and info == 2:
            obj['bytes'] = bytes(self.take(size))
            del obj['items']
            return ref
        while len(obj['items']) < size:
            value = self.primitive(info) if kind == 0 else self.value()
            if isinstance(value, dict) and 'nulls' in value:
                count = value['nulls']
                if count <= 0 or count > size - len(obj['items']):
                    raise NrbfError('Invalid null run')
                obj['items'].extend([None] * count)
            elif isinstance(value, dict) and 'end' in value:
                raise NrbfError('Unexpected end in array')
            else:
                obj['items'].append(value)
        return ref

    def record(self):
        self.record_count += 1
        if self.record_count > self.max_records or self.depth >= self.max_depth:
            raise NrbfError('Record or nesting limit exceeded')
        self.depth += 1
        try:
            return self._record()
        finally:
            self.depth -= 1

    def _record(self):
        tag = self.byte()
        if tag == 12:
            lid, name = self.integer(), self.string()
            if lid in self.libraries:
                raise NrbfError('Duplicate library ID')
            self.libraries[lid] = name
            return {'library_record': True}
        if tag in (4, 5):
            oid, name = self.integer(), self.string()
            count = self.count(self.integer())
            names = [self.string() for _ in range(count)]
            if len(set(names)) != len(names):
                raise NrbfError('Duplicate class member')
            types = [self.byte() for _ in range(count)]
            infos = [self.type_info(t) for t in types]
            lid = self.integer() if tag == 5 else None
            if lid is not None and lid not in self.libraries:
                raise NrbfError('Unknown library ID')
            metadata = {'name': name, 'names': names, 'types': types, 'infos': infos, 'library_id': lid}
            self.classes[oid] = metadata
            return self.members(oid, metadata)
        if tag == 1:
            oid, mid = self.integer(), self.integer()
            if mid not in self.classes:
                raise NrbfError('Unknown class metadata')
            return self.members(oid, self.classes[mid])
        if tag == 6:
            oid, value = self.integer(), self.string()
            return self.put(oid, value)
        if tag == 7:
            oid, shape, rank = self.integer(), self.byte(), self.integer()
            if shape not in range(6) or rank < 1 or rank > 32:
                raise NrbfError('Invalid array shape or rank')
            lengths = [self.integer() for _ in range(rank)]
            if any(n < 0 for n in lengths):
                raise NrbfError('Negative array length')
            bounds = [self.integer() for _ in range(rank)] if shape >= 3 else None
            kind = self.byte()
            return self.array(oid, lengths, kind, self.type_info(kind), bounds)
        if tag in (15, 16, 17):
            oid, size = self.integer(), self.integer()
            kind, info = (0, self.byte()) if tag == 15 else (2 if tag == 16 else 1, None)
            return self.array(oid, [size], kind, info)
        if tag == 8:
            return self.primitive(self.byte())
        if tag == 9:
            return {'ref': self.integer()}
        if tag == 10:
            return None
        if tag in (13, 14):
            return {'nulls': self.byte() if tag == 13 else self.integer()}
        if tag == 11:
            return {'end': True}
        raise NrbfError(f'Unsupported record {tag} at byte {self.pos - 1}')

    def read(self):
        if self.byte() != 0:
            raise NrbfError('Missing serialization header')
        root, header, major, minor = (self.integer() for _ in range(4))
        if (major, minor) != (1, 0):
            raise NrbfError('Unsupported stream version')
        while True:
            value = self.record()
            if value == {'end': True}:
                break
            if value is None or isinstance(value, dict) and 'nulls' in value:
                raise NrbfError('Unexpected top-level null')
        if self.pos != len(self.data):
            raise NrbfError('Trailing bytes after message end')
        if root not in self.objects:
            raise NrbfError('Root object missing')
        for obj in self.objects.values():
            values = list(obj.get('members', {}).values()) + obj.get('items', []) if isinstance(obj, dict) else []
            if any(isinstance(v, dict) and 'ref' in v and v['ref'] not in self.objects for v in values):
                raise NrbfError('Unresolved object reference')
        return {'root_id': root, 'header_id': header, 'objects': self.objects, 'libraries': self.libraries}


def inspect_nrbf(data, **limits):
    """Parse supported records, rejecting malformed/unsupported input explicitly."""
    return Reader(data, **limits).read()
