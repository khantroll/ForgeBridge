"""Code-defined native record factories; no installed/exported files needed."""
from copy import deepcopy
import io

from PIL import Image

from forgebridge.native import Node, Array, Writer
from forgebridge.native_scene_schema import CLASSES, DEFAULTS, LIBRARIES
from forgebridge.nrbf import Reader


def png(width=1, height=1):
    output = io.BytesIO()
    Image.new('RGBA', (width, height), (0, 0, 0, 0)).save(output, 'PNG')
    return output.getvalue()


def record(kind, *, image=None):
    """Build fresh typed records from member definitions/defaults, preserving aliases."""
    memo = {}
    image = png() if image is None else image
    def build(value):
        if not isinstance(value, dict): return deepcopy(value)
        if 'use' in value: return memo[value['use']]
        if 'class' in value:
            schema = deepcopy(CLASSES[value['class']])
            if set(schema['names']) != set(value['members']):
                raise ValueError('Schema/default member mismatch: ' + value['class'])
            result = Node(schema, {}, inline=value['inline'])
            memo[value['id']] = result
            result.members.update({k: build(v) for k, v in value['members'].items()})
            return result
        if 'bytes' in value:
            result = Array(list(image), 0, 2)
        else:
            kind, info = value['array']
            result = Array([], kind, deepcopy(info))
        memo[value['id']] = result
        if 'items' in value: result.items.extend(build(v) for v in value['items'])
        return result
    return build(DEFAULTS[kind])


def encode(value):
    return Writer(LIBRARIES).write(value)


def blank_map(name='Generated Geometry'):
    node = record('blank'); node.members['_name'] = name
    return encode(node)


def template_map():
    """Four native templates generated entirely from protocol definitions."""
    node = record('blank')
    tiles = node.members['_tiles'].members
    tiles['_items'].items = [record(kind) for kind in ('wall', 'door', 'light', 'image')]
    tiles.update(_size=4, _version=4)
    node.members['_nextUID'] = 5
    return encode(node)


def asset_templates():
    return encode(record('asset')), encode(record('asset_meta'))


def canonical_graph(data):
    """Root-reachable graph, with traversal IDs replacing arbitrary NRBF IDs.

    Compare class/member/type/array data and aliases. Unreachable stale records
    retained by byte-preserving patching are deliberately not scene objects.
    """
    reader = Reader(data, max_items=64000000); graph = reader.read()
    seen = {}
    def visit(oid):
        value = reader.objects[oid]
        if isinstance(value, str): return value
        if oid in seen: return {'use': seen[oid]}
        index = len(seen) + 1; seen[oid] = index
        if 'bytes' in value: return {'id': index, 'bytes': value['bytes']}
        def item(v): return visit(v['ref']) if isinstance(v, dict) and 'ref' in v else v
        if 'members' in value:
            return {'id': index, 'schema': reader.object_metadata[oid],
                    'members': {k: item(v) for k, v in value['members'].items()}}
        return {'id': index, 'array': reader.array_metadata[oid], 'lengths': value['lengths'],
                'bounds': value['lower_bounds'], 'items': [item(v) for v in value['items']]}
    return {'libraries': graph['libraries'], 'root': visit(graph['root_id'])}
