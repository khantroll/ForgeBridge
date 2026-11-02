"""Windows rename/replace comparison on caller-owned diagnostic files only.

No UI, process control, ACL/security changes or production reader changes.
"""
import ctypes
from ctypes import wintypes
import hashlib
import os


class NativeReplacementFailure(ValueError):
    def __init__(self, details):
        super().__init__('Unheld native replacement failed: ' + str(details))
        self.details = details


def process_context():
    """Read only this process's token flags; never adjust privileges."""
    if os.name != 'nt':
        return {'platform': 'not Windows'}
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    advapi = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    advapi.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    advapi.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID,
                                         wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    handle = wintypes.HANDLE()
    if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(handle)):
        return {'query_error': ctypes.get_last_error()}
    result = {}
    try:
        for name, info in (('elevation_type', 18), ('elevated', 20),
                           ('has_restrictions', 21), ('app_container', 29)):
            value, length = wintypes.DWORD(), wintypes.DWORD()
            if advapi.GetTokenInformation(handle, info, ctypes.byref(value), 4, ctypes.byref(length)):
                result[name] = value.value
            else:
                result[name+'_query_error'] = ctypes.get_last_error()
    finally:
        kernel.CloseHandle(handle)
    return result


def probe(work, *, hold_target=False):
    if os.name != 'nt':
        raise ValueError('Native replacement probe requires Windows')
    target, replacement = work / 'CURRENT', work / '000002.dbtmp'
    for path, data in ((target, b'old\n'), (replacement, b'new\n')):
        with path.open('xb') as stream:
            stream.write(data)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    move = kernel.MoveFileA
    move.argtypes = [wintypes.LPCSTR, wintypes.LPCSTR]; move.restype = wintypes.BOOL
    replace = kernel.ReplaceFileA
    replace.argtypes = [wintypes.LPCSTR, wintypes.LPCSTR, wintypes.LPCSTR,
                        wintypes.DWORD, wintypes.LPVOID, wintypes.LPVOID]
    replace.restype = wintypes.BOOL
    create = kernel.CreateFileW
    create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                       wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    create.restype = wintypes.HANDLE
    close = kernel.CloseHandle
    close.argtypes = [wintypes.HANDLE]; close.restype = wintypes.BOOL
    handle = None
    try:
        if hold_target:
            # Deliberately deny delete sharing for our own CURRENT file. This is
            # a mechanism control, not evidence that another process did this.
            handle = create(str(target), 0x80000000, 1 | 2, None, 3, 0x80, None)
            if handle == ctypes.c_void_p(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
        moved = bool(move(str(replacement).encode('mbcs'), str(target).encode('mbcs')))
        move_error = 0 if moved else ctypes.get_last_error()
        replaced, replace_error = False, 0
        if not moved:
            replaced = bool(replace(str(target).encode('mbcs'), str(replacement).encode('mbcs'),
                                    None, 2, None, None))
            replace_error = 0 if replaced else ctypes.get_last_error()
        row = {'held_without_delete_sharing': hold_target, 'move_ok': moved,
               'move_error': move_error, 'replace_ok': replaced, 'replace_error': replace_error,
               'target_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
               'replacement_exists': replacement.exists()}
        if hold_target:
            if moved or replaced or target.read_bytes() != b'old\n' or not replacement.exists():
                raise ValueError('Held-target control did not preserve the blocked replacement')
            row['expected_block_observed'] = True
        elif not (moved or replaced) or target.read_bytes() != b'new\n':
            raise NativeReplacementFailure(row)
        return row
    finally:
        if handle is not None and handle != ctypes.c_void_p(-1).value:
            close(handle)


def main():
    # Standalone mode deliberately imports neither plyvel nor ForgeBridge.
    import argparse
    import json
    from pathlib import Path
    import platform
    import time
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, help='New directory; all trial files retained')
    parser.add_argument('--trials', type=int, choices=range(1,31), default=10)
    args = parser.parse_args()
    root = Path(args.out).absolute()
    root.mkdir(parents=True, exist_ok=False)
    report = {'format': 'forgebridge.windows-replace-probe', 'version': 1,
              'python': platform.python_version(), 'process_context': process_context(),
              'scope': 'Standalone native file APIs, no LevelDB import or calls', 'operations': []}
    for held in (False, True):
        for trial in range(args.trials):
            work = root / (('held-' if held else 'free-') + str(trial))
            work.mkdir()
            row = {'held': held, 'trial': trial+1, 'status': 'FAIL'}
            started = time.monotonic()
            try:
                row.update(probe(work, hold_target=held))
                row['status'] = 'PASS'
            except (OSError, ValueError) as exc:
                row.update(error_type=type(exc).__name__, error=str(exc))
                row.update(getattr(exc, 'details', {}))
            row['seconds'] = round(time.monotonic()-started,4)
            report['operations'].append(row)
            (root/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    totals = {mode: {status: sum(r['held'] == held and r['status'] == status
                              for r in report['operations']) for status in ('PASS','FAIL')}
              for mode,held in (('free',False),('held',True))}
    report['totals'] = totals
    (root/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'totals':totals,'process_context':report['process_context']},indent=2))
    return int(any(row['status']=='FAIL' for row in report['operations']))


if __name__ == '__main__':
    raise SystemExit(main())
