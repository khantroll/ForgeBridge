"""Foundry source adapter for the bounded placed-token slice."""
import math

from forgebridge.token_ir import Token
from forgebridge.uvtt import _scene_origin


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('Expected finite token number')
    return float(value)


def scene_tokens(scene):
    """Return IR tokens and explicit per-token refusals; never execute flags/scripts."""
    grid = scene.get('grid', {})
    if not isinstance(grid, dict) or not isinstance(scene.get('_id'), str) or not scene['_id']:
        raise ValueError('Token slice requires source scene identity and grid')
    size = number(grid.get('size'))
    if size <= 0 or grid.get('type') != 1:
        raise ValueError('Token slice requires a positive square source grid')
    origin = _scene_origin(scene, size, [])
    raw = scene.get('tokens', [])
    if not isinstance(raw, list) or len(raw) > 256:
        raise ValueError('Token slice supports at most 256 tokens')
    result, rejected, seen = [], [], set()
    mapped = {'_id', 'name', 'texture', 'x', 'y', 'width', 'height', 'rotation', 'hidden'}
    for item in raw:
        try:
            identity = item['_id']
            if not isinstance(identity, str) or not identity or len(identity) > 256 or identity in seen:
                raise ValueError('Missing or duplicate source token identity')
            seen.add(identity)
            width, height = number(item['width']), number(item['height'])
            if width != height or not 0 < width <= 32:
                raise ValueError('Only square footprints up to 32 squares are supported')
            texture = item['texture']
            path = texture['src']
            if not isinstance(path, str) or not path:
                raise ValueError('Missing token texture')
            sx, sy = number(texture.get('scaleX', 1)), number(texture.get('scaleY', 1))
            if not 0 < sx <= 1 or not 0 < sy <= 1:
                raise ValueError('Texture scale must be positive and at most one; no clipping or mirroring guesses')
            for key, default in [('anchorX', .5), ('anchorY', .5), ('offsetX', 0),
                                 ('offsetY', 0), ('rotation', 0), ('tint', '#ffffff'), ('fit', 'contain')]:
                if texture.get(key, default) != default:
                    raise ValueError(f'Unsupported texture.{key}')
            if type(item.get('hidden', False)) is not bool:
                raise ValueError('Token hidden must be boolean')
            name = item.get('name') or identity
            if not isinstance(name, str) or len(name) > 256:
                raise ValueError('Invalid token name')
            retained = sorted(set(item) - mapped)
            retained.extend('texture.' + key for key in sorted(set(texture) - {
                'src', 'scaleX', 'scaleY', 'anchorX', 'anchorY', 'offsetX', 'offsetY', 'rotation', 'tint', 'fit'}))
            result.append(Token('Scene.' + scene['_id'] + '.Token.' + identity, name, path,
                ((number(item['x']) - origin[0]) / size + width / 2,
                 (number(item['y']) - origin[1]) / size + height / 2),
                (width, height), (sx, sy), number(item.get('rotation', 0)),
                item.get('hidden', False), tuple(retained)))
        except (KeyError, TypeError, ValueError) as exc:
            rejected.append({'source_id': item.get('_id') if isinstance(item, dict) else None,
                             'status': 'unsupported', 'reason': str(exc)})
    return result, rejected
