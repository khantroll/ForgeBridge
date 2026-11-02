import struct
import unittest
from forgebridge.nrbf import NrbfError, inspect_nrbf


def i(n):
    return struct.pack('<i', n)


def s(text):
    data = text.encode('utf-8')
    size, prefix = len(data), bytearray()
    while size >= 128:
        prefix.append((size & 127) | 128)
        size >>= 7
    return bytes(prefix) + bytes([size]) + data


def stream(body, root=1):
    return b'\0' + i(root) + i(-1) + i(1) + i(0) + body + b'\x0b'


def cls(oid, names, types, infos=b''):
    return b'\x04' + i(oid) + s('SyntheticClass') + i(len(names)) + b''.join(s(n) for n in names) + bytes(types) + infos


class NrbfTests(unittest.TestCase):
    def test_forward_references_and_cycles_remain_ids(self):
        body = cls(1, ['text', 'self'], [1, 2]) + b'\x09' + i(2) + b'\x09' + i(1) + b'\x06' + i(2) + s('Hello')
        g = inspect_nrbf(stream(body))
        self.assertEqual(g['objects'][1]['members'], {'text': {'ref': 2}, 'self': {'ref': 1}})
        self.assertEqual(g['objects'][2], 'Hello')

    def test_metadata_reuse_and_inline_primitives(self):
        body = cls(1, ['number'], [0], b'\x08') + i(42) + b'\x01' + i(2) + i(1) + i(-7)
        g = inspect_nrbf(stream(body))
        self.assertEqual(g['objects'][2]['members']['number'], -7)

    def test_object_array_null_runs(self):
        g = inspect_nrbf(stream(b'\x10' + i(1) + i(4) + b'\x0d\x03\x06' + i(2) + s('tail')))
        self.assertEqual(g['objects'][1]['items'], [None, None, None, {'ref': 2}])

    def test_primitive_byte_array_and_rectangular_array(self):
        g = inspect_nrbf(stream(b'\x0f' + i(1) + i(3) + b'\x02abc'))
        self.assertEqual(g['objects'][1]['bytes'], b'abc')
        body = b'\x07' + i(1) + bytes([2]) + i(2) + i(2) + i(2) + b'\x00\x08' + b''.join(i(x) for x in range(4))
        self.assertEqual(inspect_nrbf(stream(body))['objects'][1]['items'], [0, 1, 2, 3])

    def test_every_truncated_prefix_is_rejected(self):
        data = stream(cls(1, ['value'], [1]) + b'\x06' + i(2) + s('a' * 150))
        for cut in range(len(data)):
            with self.subTest(cut=cut), self.assertRaises(NrbfError):
                inspect_nrbf(data[:cut])

    def test_limits(self):
        data = stream(b'\x10' + i(1) + i(2) + b'\x0a\x0a')
        for limits in ({'max_bytes': 1}, {'max_items': 1}, {'max_records': 1}, {'max_depth': 1}):
            with self.subTest(limits=limits), self.assertRaises(NrbfError):
                inspect_nrbf(data, **limits)

    def test_invalid_null_runs_counts_and_references(self):
        bodies = [b'\x10' + i(1) + i(2) + b'\x0d\x03',
                  b'\x10' + i(1) + i(-1),
                  cls(1, ['x'], [2]) + b'\x09' + i(999),
                  b'\x06' + i(1) + s('x') + b'\x06' + i(1) + s('y')]
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(NrbfError):
                inspect_nrbf(stream(body))

    def test_unsupported_records_and_trailing_data(self):
        for data in (stream(b'\x15'), stream(b'\x06' + i(1) + s('x')) + b'extra'):
            with self.assertRaises(NrbfError):
                inspect_nrbf(data)

    def test_libraries_are_inert_strings(self):
        body = b'\x0c' + i(7) + s('Untrusted.Assembly') + b'\x05' + i(1) + s('Untrusted.Type') + i(0) + i(7)
        g = inspect_nrbf(stream(body))
        self.assertEqual(g['libraries'][7], 'Untrusted.Assembly')
        self.assertEqual(g['objects'][1]['class'], 'Untrusted.Type')
