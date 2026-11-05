"""Portable visible names; source and internal native identities stay separate."""
import re


def sanitize_name(value):
    if not isinstance(value, str):
        raise ValueError('Names must be text')
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f-\x9f]', '', value).rstrip('. ')
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
    if not 1 <= len(name) <= 80:
        raise ValueError('Names must contain 1–80 characters after Windows sanitization')
    if name.split('.')[0].rstrip().upper() in reserved:
        raise ValueError('Reserved Windows name: ' + name)
    return name


def default_folder(row, package_title=None):
    retained = row.get('retained_fields')
    parent = retained.get('_forgebridge_parent_adventure') if isinstance(retained, dict) else None
    parent_name = parent.get('name') if isinstance(parent, dict) else None
    for candidate in (row.get('parent_adventure_name'), parent_name, package_title):
        if isinstance(candidate, str) and candidate.strip():
            return sanitize_name(candidate)
    return 'ForgeBridge'


def plan_names(rows, package_title=None, *, map_folder=None, notes_folder=None, map_names=None):
    from forgebridge.convert import scene_key
    keys = [r.get('key') or scene_key(r) for r in rows]
    overrides = {}
    entries = map_names.items() if isinstance(map_names, dict) else (map_names or [])
    for entry in entries:
        if isinstance(entry, tuple):
            key, value = entry
        elif '=' in entry:
            key, value = entry.split('=', 1)
        elif len(keys) == 1:
            key, value = keys[0], entry
        else:
            raise ValueError('Use --map-name SCENE_KEY=NAME for multiple scenes')
        if key not in keys or key in overrides:
            raise ValueError('Unknown or repeated --map-name scene key: ' + key)
        overrides[key] = value
    plans, used = {}, {}
    for row, key in zip(rows, keys):
        folder = sanitize_name(map_folder) if map_folder is not None else default_folder(row, package_title)
        name = sanitize_name(overrides.get(key, row.get('name') or row['id']))
        # Collisions are per destination folder; the same scene name in two
        # adventures is fine when each adventure becomes its own map folder.
        collision = (folder.casefold(), name.casefold())
        if collision in used:
            raise ValueError(f'Map name conflict: {name!r} for {used[collision]} and {key}. '
                             'Rename with --map-name SCENE_KEY=NAME; no hash is added automatically.')
        used[collision] = key
        plans[key] = {'map_folder': folder, 'map_name': name,
                      'notes_folder': sanitize_name(notes_folder) if notes_folder is not None else folder,
                      'map_path': f'MyAssets/Maps/{folder}/{name}.rwmap'}
    return plans
