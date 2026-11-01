"""Double-click launcher from a source checkout; no installed content touched."""
from pathlib import Path
import sys
import os

if __name__ == '__main__':
    checkout = Path(__file__).resolve().parent
    interpreter = checkout / '.venv/Scripts/pythonw.exe'
    # Use the environment created by the operator guide rather than the .pyw
    # file association's potentially different Python/dependency installation.
    if interpreter.is_file() and interpreter.resolve() != Path(sys.executable).resolve():
        os.execv(str(interpreter), [str(interpreter), str(Path(__file__).resolve()), *sys.argv[1:]])
    sys.path.insert(0, str(checkout / 'src'))
    try:
        from forgebridge.gui import main
        raise SystemExit(main())
    except ImportError as exc:
        import tkinter.messagebox
        tkinter.messagebox.showerror('ForgeBridge setup required',
            'Install the dependencies using docs/USER-GUIDE.md, then reopen this launcher.\n\n' + str(exc))
