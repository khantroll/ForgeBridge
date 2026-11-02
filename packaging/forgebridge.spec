# Two one-folder executables sharing one _internal directory (never one-file).
import json
import os
import sys
from pathlib import Path
from importlib.metadata import version
from PyInstaller.utils.hooks import (
    collect_data_files, collect_dynamic_libs, collect_submodules, copy_metadata,
    collect_delvewheel_libs_directory,
)

root = Path(SPECPATH).parent
build_version = version('forgebridge')
info = Path(workpath) / 'build-info.json'
info.parent.mkdir(parents=True, exist_ok=True)
info.write_text(json.dumps({'version': build_version, 'mode': 'onedir', 'architecture': 'windows-x64'}), encoding='utf-8')
datas = [(source, dest) for source, dest in collect_data_files('forgebridge')
         if not dest.replace('\\', '/').startswith('forgebridge/schema')]
for distribution in ('forgebridge', 'Pillow', 'plyvel-next', 'pypdfium2', 'psutil', 'pyinstaller'):
    datas += copy_metadata(distribution)  # Includes dependency license notices.
python_license = Path(sys.base_prefix) / 'LICENSE.txt'
if python_license.is_file():
    datas += [(str(python_license), 'licenses/python')]
datas += [(str(p), 'forgebridge/schema') for p in (root / 'schema').glob('*.json')]
datas += [(str(info), 'forgebridge')]
datas += collect_data_files('pypdfium2_raw') + collect_data_files('pypdfium2') + collect_data_files('pypdfium2_cfg')
binary_data, binaries = collect_delvewheel_libs_directory('plyvel_next')
datas += binary_data
binaries += collect_dynamic_libs('pypdfium2_raw')
hidden = ['plyvel_next', 'psutil', 'tkinter', 'tkinter.filedialog', 'tkinter.messagebox', 'gui_smoke']
hidden += collect_submodules('pypdfium2', filter=lambda n: '.tests' not in n)
common = dict(pathex=[str(root / 'src'), str(root / 'packaging')], binaries=binaries, datas=datas,
              hiddenimports=hidden, excludes=['pytest', 'unittest', 'PIL.ImageQt', 'numpy', 'IPython'],
              noarchive=False)
gui_a = Analysis([str(root / 'packaging/gui_entry.py')], **common)
cli_a = Analysis([str(root / 'packaging/cli_entry.py')], **common)
gui = EXE(PYZ(gui_a.pure), gui_a.scripts, [], exclude_binaries=True, name='ForgeBridge',
          console=False, debug=False, strip=False, upx=False, contents_directory='_internal')
cli = EXE(PYZ(cli_a.pure), cli_a.scripts, [], exclude_binaries=True, name='forgebridge-cli',
          console=True, debug=False, strip=False, upx=False, contents_directory='_internal')
bundle = COLLECT(gui, cli, gui_a.binaries, gui_a.datas, cli_a.binaries, cli_a.datas,
                 strip=False, upx=False, name='ForgeBridge')
