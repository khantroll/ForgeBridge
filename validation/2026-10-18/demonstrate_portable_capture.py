"""File-only demonstration; private assets stay in a caller-selected new folder."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil

from forgebridge.native_capture import portable_profile
from forgebridge.scene_profile import load_profile, preflight_profile, fingerprint
from forgebridge.scene_profile import _inputs
from forgebridge.package import build_package


def validate_checkpoint(expected, found):
    def normalized(profile):
        profile = deepcopy(profile)
        for _, item in _inputs(profile):
            item.pop('path')
        return profile
    if normalized(expected) != normalized(found):
        raise ValueError('Checkpoint settings differ from the source profile; choose a new output directory')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profiles', nargs=2, required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--resume', action='store_true', help='Validate and reuse completed capture checkpoints')
    parser.add_argument('--build-scenes', action='store_true', help='Optional additional full package compilation')
    args = parser.parse_args()
    root = Path(args.out).resolve()
    root.mkdir(parents=True, exist_ok=args.resume)
    reports = []
    for index, source in enumerate(args.profiles):
        p, _, _ = load_profile(source)
        destination = root / str(index)
        moved = root / ('relocated-' + str(index))
        if any(path.is_symlink() or path.resolve() != root / path.name for path in (destination, moved)):
            raise ValueError('Capture checkpoint leaves the selected output directory')
        if not (args.resume and moved.exists()):
            print('Capturing '+p['output']['map_name'], flush=True)
            portable_profile(source, destination)
            shutil.move(destination, moved)
        relocated, _, _ = load_profile(moved/'scene-profile.json')
        validate_checkpoint(p, relocated)
        package_hash = None
        if args.build_scenes:
            report, settings = preflight_profile(moved/'scene-profile.json')
            package = root / ('scene-' + str(index) + '.zip')
            build_package(**settings, dest=package, profile_provenance=report['provenance'])
            package_hash = fingerprint(package)
        manifest = json.loads((moved/'capture/manifest.json').read_text(encoding='utf-8'))
        reports.append({'scene': p['source']['scene_id'], 'map': p['output']['map_name'],
                        'input_validation': 'PASS', 'capture_files': len(manifest['files']),
                        'capture_sha256': manifest['bundle_sha256'],
                        'optional_package_sha256': package_hash,
                        'runtime_validation': 'not performed'})
    (root/'results.json').write_text(json.dumps(reports, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(reports, indent=2))


if __name__ == '__main__':
    main()
