"""Visible GUI failures with local traceback logs, including windowed builds."""
from datetime import datetime, timezone
import os
from pathlib import Path
import tempfile
import traceback


def error_log(details, output=None):
    candidates = []
    if output:
        candidates.append(Path(output).absolute().parent)
    candidates.append(Path(os.environ.get('LOCALAPPDATA', tempfile.gettempdir())) / 'ForgeBridge')
    for directory in candidates:
        path = directory / 'forgebridge-error.log'
        try:
            if any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)):
                continue
            directory.mkdir(parents=True, exist_ok=True)
            with path.open('a', encoding='utf-8') as stream:
                stream.write(f'\n{datetime.now(timezone.utc).isoformat()}\n{details}\n')
            return path
        except OSError:
            continue
    return None


def report_error(message, details, *, output=None, show=None):
    log = error_log(details, output)
    text = str(message) + ('\n\nDetails: ' + str(log) if log else '\n\nThe error log could not be written.')
    if show is None:
        from tkinter import messagebox
        show = messagebox.showerror
    show('ForgeBridge', text)
    return log


def startup_error(exc):
    details = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    try:
        from tkinter import Tk, messagebox
        root = Tk(); root.withdraw()
        try: report_error(str(exc), details, show=messagebox.showerror)
        finally: root.destroy()
    except Exception:
        log = error_log(details)
        # Last resort if Tk itself cannot initialize in a Windows windowed build.
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, str(exc) + '\nLog: ' + str(log), 'ForgeBridge', 0x10)
