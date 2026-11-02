"""Bounded frozen-GUI diagnostics; no Toolkit, installation, or source imports."""
import json
from pathlib import Path
import queue
import threading
import traceback


def check(destination):
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from forgebridge.gui_errors import report_error
    from forgebridge.version import get_version
    import psutil
    dest = Path(destination).absolute()
    if dest.exists(): raise ValueError('Bundle-check output must be new')
    root = tk.Tk(); root.withdraw()
    root.title('ForgeBridge ' + get_version() + ' — scene conversion')
    result = {'version': get_version(), 'title': root.title(), 'tcl': root.tk.call('info', 'patchlevel'),
              'psutil_pid': psutil.Process().pid}
    try:
        # Exercise real Tk file-picker widgets without a modal OS dialog in CI.
        fixture = dest.parent / 'gui-picker-fixture.txt'; fixture.write_text('synthetic picker input')
        dialog = filedialog.LoadFileDialog(root)
        dialog.top.withdraw(); dialog.directory = str(dest.parent)
        dialog.set_filter(str(dest.parent), '*'); dialog.filter_command()
        dialog.set_selection(fixture.name); dialog.ok_command()
        assert Path(dialog.how) == fixture
        dialog.top.destroy(); result['tk_file_picker_selection'] = 'PASS'
        # Native dialog commands must exist; invalid options refuse before UI.
        for command in ('tk_getOpenFile', 'tk_getSaveFile', 'tk_chooseDirectory', 'tk_messageBox'):
            try: root.tk.call(command, '-forgebridge-invalid-option', '1')
            except tk.TclError as exc:
                assert 'invalid command name' not in str(exc), str(exc)
            else: raise AssertionError('Dialog command accepted an invalid option: ' + command)
        result['native_dialog_commands'] = 'PASS (argument validation; no manual modal interaction)'
        messages, jobs = [], queue.Queue()
        show = lambda title, text: messages.append((title, text))
        def callback_error(kind, value, tb):
            report_error(str(value), ''.join(traceback.format_exception(kind, value, tb)),
                         output=dest.parent / 'converted-output', show=show)
        root.report_callback_exception = callback_error
        def worker():
            try: raise RuntimeError('synthetic worker failure')
            except Exception as exc: jobs.put((str(exc), traceback.format_exc()))
        threading.Thread(target=worker).start()
        def pump():
            try: message, details = jobs.get_nowait()
            except queue.Empty: root.after(20, pump); return
            report_error(message, details, output=dest.parent / 'converted-output', show=show)
            result['worker_thread'] = 'PASS'
            root.after(0, lambda: 1 / 0)
            root.after(100, root.quit)
        root.after(0, pump); root.after(10000, root.quit); root.mainloop()
        assert result.get('worker_thread') == 'PASS'
        assert len(messages) == 2, messages
        assert 'synthetic worker failure' in messages[0][1]
        assert 'division by zero' in messages[1][1]
        log = dest.parent / 'forgebridge-error.log'
        assert 'Traceback' in log.read_text(encoding='utf-8')
        result.update(error_dialog_dispatch='PASS (captured, no blocking modal)', error_log=str(log), status='PASS')
        with dest.open('x', encoding='utf-8') as stream: json.dump(result, stream, indent=2)
    finally:
        root.destroy()
