"""Small local Tk front end over the public conversion and add-only install APIs."""
import argparse
from pathlib import Path
import queue
import threading
import uuid

from forgebridge.convert import discover, convert
from forgebridge.installer import install, native_outputs


def install_outputs(report, output, myassets, backups):
    return install(native_outputs(report, output), myassets, backups)


def report_text(value):
    """Readable stage-specific loss summary; detailed JSON remains in output."""
    if 'scenes' in value:
        lines = [f"Scenes: {len(value['scenes'])}"]
        if 'status' in value: lines.append('Conversion outcome: ' + value['status'])
        if 'counts' in value:
            lines.append('Source/UVTT stage: ' + ', '.join(f'{grade}: {count}' for grade, count in value['counts'].items()))
        for scene in value['scenes']:
            lines += ['', f"{scene.get('name') or scene.get('id')}: {scene.get('status', 'discovered')}"]
            if scene.get('error'): lines.append('Needs attention: ' + scene['error'])
            if scene.get('artifact'): lines.append('Output: ' + scene['folder'] + '/' + scene['artifact'])
            if scene.get('native_report'):
                lines.append('Native package: ' + ', '.join(f'{k}: {v}' for k, v in scene['native_report']['counts'].items()))
        if value.get('manual_steps'): lines += ['', 'Manual requirements:', *value['manual_steps']]
        lines += ['', 'Generating files does not prove Toolkit behavior. Review conversion-report.json for full losses.']
        return '\n'.join(lines)
    return '\n'.join(f'{key}: {val}' for key, val in value.items())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', default='')
    parser.add_argument('--out', default='')
    args = parser.parse_args(argv)
    # Lazy import: headless CI exercises the controller without creating a window.
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    app = tk.Tk(); app.title('ForgeBridge — scene conversion'); app.geometry('900x720')
    package = tk.StringVar(value=args.package); output = tk.StringVar(value=args.out)
    status = tk.StringVar(value='Select a Foundry folder or ZIP, then discover scenes.')
    profiles, rows, jobs = [], [], queue.Queue()
    state = {'busy': False, 'report': None, 'output': None, 'source': None}
    panel = ttk.Frame(app, padding=12); panel.pack(fill='both', expand=True)
    ttk.Label(panel, text='Foundry package').pack(anchor='w')
    ttk.Entry(panel, textvariable=package).pack(fill='x')
    buttons = ttk.Frame(panel); buttons.pack(fill='x', pady=5)
    ttk.Button(buttons, text='Choose folder', command=lambda: package.set(filedialog.askdirectory() or package.get())).pack(side='left')
    ttk.Button(buttons, text='Choose ZIP', command=lambda: package.set(filedialog.askopenfilename(filetypes=[('Foundry ZIP', '*.zip')]) or package.get())).pack(side='left')
    ttk.Label(panel, text='New output folder (must not exist)').pack(anchor='w')
    ttk.Entry(panel, textvariable=output).pack(fill='x')
    ttk.Button(panel, text='Choose output parent', command=lambda: choose_output()).pack(anchor='w', pady=4)
    ttk.Label(panel, text='Scenes — select one or more (pack/Adventure scope is preserved)').pack(anchor='w')
    scenes = tk.Listbox(panel, selectmode='extended', exportselection=False, height=9)
    scenes.pack(fill='x')
    controls = ttk.Frame(panel); controls.pack(fill='x', pady=6)
    profile_label = tk.StringVar(value='Schema-built native output. Existing calibrated profiles are optional overrides.')
    ttk.Label(panel, textvariable=profile_label, wraplength=850).pack(anchor='w')
    ttk.Label(panel, textvariable=status, wraplength=850).pack(anchor='w', pady=6)
    text = tk.Text(panel, wrap='word', height=15); text.pack(fill='both', expand=True)

    def choose_output():
        chosen = filedialog.askdirectory()
        if chosen: output.set(str(Path(chosen) / ('ForgeBridge-output-' + uuid.uuid4().hex[:8])))

    def start(function, done):
        if state['busy']: return
        state['busy'] = True; status.set('Working locally. Keep inputs unchanged; wait for completion.')
        def worker():
            try: jobs.put((done, function(), None))
            except Exception as exc: jobs.put((done, None, str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def display(value):
        text.delete('1.0', 'end'); text.insert('1.0', report_text(value))

    def found(report, source):
        rows[:] = report['scenes']; scenes.delete(0, 'end')
        for row in rows:
            scenes.insert('end', f"{row.get('name') or row['id']} | {row['source_path']} | Adventure {row['parent_adventure_id'] or '—'}")
        scenes.selection_set(0, 'end'); state['source'] = source
        status.set(f'{len(rows)} scenes found. Choose output and build; then review the loss report.')
        display(report)

    def find():
        source = package.get()
        if not source: messagebox.showerror('Source required', 'Select a Foundry package first.'); return
        if state['busy']: return
        state['report'] = None; install_button.configure(state='disabled')
        start(lambda: discover(source), lambda report: found(report, source))

    def profiles_pick():
        if state['busy']: return
        chosen = filedialog.askopenfilenames(filetypes=[('Scene profiles', '*.json')])
        if chosen:
            profiles[:] = chosen
            profile_label.set(f'{len(profiles)} existing profiles selected. Other scenes use schema-built native synthesis.')

    def built(report):
        state['report'] = report
        display(report)
        status.set(f"{report['status']}: review combined losses. Output: {state['output']}")
        try: native_outputs(report, state['output']); install_button.configure(state='normal')
        except ValueError: install_button.configure(state='disabled')

    def build():
        if state['busy']: return
        if state['source'] != package.get():
            messagebox.showerror('Rediscover scenes', 'The package changed; click Discover first.'); return
        selected = [rows[i]['key'] for i in scenes.curselection()]
        if not selected or not output.get():
            messagebox.showerror('Selection required', 'Choose scenes and a new output folder.'); return
        source, dest, controls = package.get(), output.get(), list(profiles)
        state['build_source'] = source
        state['output'] = dest; state['report'] = None; install_button.configure(state='disabled')
        start(lambda: convert(source, dest, scene_keys=selected, profiles=controls), built)

    def install_selected():
        if state['busy'] or not state['report']: return
        if state.get('build_source') != package.get():
            messagebox.showerror('Source changed', 'Review/build the current source before installing.'); return
        report, dest = state['report'], state['output']
        try: packages = native_outputs(report, dest)
        except ValueError as exc:
            messagebox.showerror('Native output unavailable', str(exc)); return
        target = filedialog.askdirectory(title='Select actual MyAssets (Toolkit must be closed)')
        if not target: return
        backups = filedialog.askdirectory(title='Select separate existing backup directory')
        if not backups: return
        if not messagebox.askyesno('Review add-only installation',
            f'Install {len(packages)} native packages from {len(report["scenes"])} scene results?\n'
            f'MyAssets: {target}\nBackups: {backups}\n\n'
            'Read the loss report first. Toolkit must stay closed. A full backup is made; conflicts refuse all copying. '
            'Manual UVTT scenes are not installed.'): return
        def installed(result):
            display(result); status.set('Added native files. Backup/uninstall receipt shown. No Toolkit validation performed.')
        start(lambda: install_outputs(report, dest, target, backups), installed)

    ttk.Button(controls, text='Discover scenes', command=find).pack(side='left')
    ttk.Button(controls, text='Optional profiles', command=profiles_pick).pack(side='left')
    ttk.Button(controls, text='Build / export', command=build).pack(side='left')
    install_button = ttk.Button(controls, text='Install reviewed native outputs', command=install_selected, state='disabled')
    install_button.pack(side='left')

    def pump():
        try:
            done, value, error = jobs.get_nowait(); state['busy'] = False
            if error:
                status.set('Failed; inspect the message and any incomplete output before retrying.')
                messagebox.showerror('ForgeBridge', error)
            else: done(value)
        except queue.Empty: pass
        app.after(150, pump)

    def close():
        if state['busy']:
            messagebox.showinfo('Operation in progress', 'Wait for the file operation to finish before closing.'); return
        app.destroy()
    app.protocol('WM_DELETE_WINDOW', close)
    app.after(150, pump); app.mainloop()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
