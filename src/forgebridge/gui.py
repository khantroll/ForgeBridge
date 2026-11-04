"""Small local Tk front end over the public conversion and add-only install APIs."""
import argparse
import math
from pathlib import Path
import queue
import threading
import traceback
import uuid

from forgebridge.convert import discover, convert
from forgebridge.installer import install, native_outputs
from forgebridge.install_review import review
from forgebridge.output_names import default_folder, sanitize_name, plan_names
from forgebridge.version import get_version
from forgebridge.gui_errors import report_error


def install_outputs(report, output, myassets, backups):
    return install(native_outputs(report, output), myassets, backups)


def scene_label(row):
    if row.get('source_type') == 'fantasy_grounds':
        grid = f"; {row['pixels_per_square']:g} px/square" if row.get('pixels_per_square') else ''
        supplied = '; ' + row['grid_supplied'] if row.get('grid_supplied') else ''
        return f"{row.get('name') or row['id']} — {row['module_name']} [{row['status']}{grid}{supplied}]"
    pack = Path(row.get('source_path') or '').name
    adventure = row.get('parent_adventure_name')
    return f"{row.get('name') or row['id']} — {adventure} ({pack})" if adventure else f"{row.get('name') or row['id']} — {pack}"


def populate_scenes(widget, report):
    """Keep displayed order and key lookup together; discovery selects nothing."""
    rows = sorted(report['scenes'], key=lambda row: (
        (row.get('parent_adventure_name') or Path(row.get('source_path') or '').name).casefold(),
        row.get('source_path') or '', row.get('parent_adventure_id') or '',
        (row.get('name') or row['id']).casefold(), row['key']))
    widget.delete(0, 'end')
    for row in rows:
        widget.insert('end', scene_label(row))
    widget.selection_clear(0, 'end')
    return rows


def report_text(value):
    """Readable stage-specific loss summary; detailed JSON remains in output."""
    if 'scenes' in value:
        lines = [f"Scenes: {len(value['scenes'])}"]
        if value.get('source_type') == 'fantasy_grounds':
            module = value.get('module_definition', {})
            lines.append('Fantasy Grounds module: ' + str(module.get('displayname') or module.get('name')))
            if value.get('hidden_art'): lines.append(f"Artwork hidden: {value['hidden_art']} (Include artwork to list it)")
        if value.get('pdf_mode'):
            lines.append('PDF mode: ' + value['pdf_mode'])
        if value.get('pdf_mode_loss'):
            lines.append('PDF loss: ' + value['pdf_mode_loss'])
        if 'status' in value: lines.append('Conversion outcome: ' + value['status'])
        if 'counts' in value:
            lines.append('Source/UVTT stage: ' + ', '.join(f'{grade}: {count}' for grade, count in value['counts'].items()))
        for campaign in value.get('campaign_content', []):
            lines.append('Campaign content: ' + ', '.join(f'{kind}: {count}' for kind,count in campaign['counts'].items()))
            lines += [f"{loss['grade']}: {loss['feature']} — {loss['summary']}" for loss in campaign['losses']]
        for scene in value['scenes']:
            lines += ['', f"{scene.get('name') or scene.get('id')}: {scene.get('status', 'discovered')}"]
            if scene.get('error'): lines.append('Needs attention: ' + scene['error'])
            fg = scene.get('fantasy_grounds')
            if fg:
                lines.append('FG counts: ' + ', '.join(f'{k}: {v}' for k, v in fg['counts'].items()))
                lines.append(f"Metadata: {fg['metadata_source']}; pixels/square: {fg['pixels_per_square']:g}; resampling: {fg['resampling']}")
                lines += [f"{loss['grade']}: {loss['field']} — {loss['detail']}" for loss in fg['losses']]
            if scene.get('artifact'): lines.append('Output: ' + scene['folder'] + '/' + scene['artifact'])
            if scene.get('native_report'):
                records = scene['native_report'].get('native_synthesis', {}).get('records')
                if records: lines.append('Native records: ' + ', '.join(f'{k}: {v}' for k, v in records.items()))
                if scene['native_report'].get('output_names'):
                    names = scene['native_report']['output_names']
                    lines.append(f"Map: {names['map_path']}\nNotes folder: {names['notes_folder']}")
                lines.append('Native package: ' + ', '.join(f'{k}: {v}' for k, v in scene['native_report']['counts'].items()))
        if value.get('manual_steps'): lines += ['', 'Manual requirements:', *value['manual_steps']]
        lines += ['', 'Generating files does not prove Toolkit behavior. Review conversion-report.json for full losses.']
        return '\n'.join(lines)
    return '\n'.join(f'{key}: {val}' for key, val in value.items())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='version', version='ForgeBridge ' + get_version())
    parser.add_argument('--package', default='')
    parser.add_argument('--out', default='')
    parser.add_argument('--dnd5e-system', default='')
    args = parser.parse_args(argv)
    # Lazy import: headless CI exercises the controller without creating a window.
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog, ttk
    app = tk.Tk(); app.title('ForgeBridge ' + get_version() + ' — scene conversion'); app.geometry('900x860')
    package = tk.StringVar(value=args.package); output = tk.StringVar(value=args.out)
    spell_input = tk.StringVar(value=args.dnd5e_system)
    map_folder, notes_folder = tk.StringVar(), tk.StringVar()
    pdf_pages = tk.BooleanVar(value=True)
    include_art = tk.BooleanVar(value=False)
    grids, across = {}, {}
    renamed = {}
    status = tk.StringVar(value='Select a Foundry package or Fantasy Grounds module, then discover scenes.')
    profiles, rows, jobs = [], [], queue.Queue()
    state = {'busy': False, 'report': None, 'output': None, 'source': None}
    def callback_error(kind, value, tb):
        report_error(str(value), ''.join(traceback.format_exception(kind, value, tb)), output=output.get())
    app.report_callback_exception = callback_error
    panel = ttk.Frame(app, padding=12); panel.pack(fill='both', expand=True)
    ttk.Label(panel, text='Foundry package / Fantasy Grounds module').pack(anchor='w')
    ttk.Entry(panel, textvariable=package).pack(fill='x')
    buttons = ttk.Frame(panel); buttons.pack(fill='x', pady=5)
    ttk.Button(buttons, text='Choose folder', command=lambda: package.set(filedialog.askdirectory() or package.get())).pack(side='left')
    ttk.Button(buttons, text='Choose ZIP', command=lambda: package.set(filedialog.askopenfilename(filetypes=[('Foundry ZIP', '*.zip')]) or package.get())).pack(side='left')
    ttk.Button(buttons, text='Choose FG module', command=lambda: package.set(filedialog.askopenfilename(
        filetypes=[('Fantasy Grounds module or vault ZIP', '*.mod *.zip *.dat')]) or package.get())).pack(side='left')
    ttk.Label(panel, text='Optional dnd5e system folder / spells pack (Foundry only)').pack(anchor='w')
    ttk.Entry(panel, textvariable=spell_input).pack(fill='x')
    spell_buttons = ttk.Frame(panel); spell_buttons.pack(fill='x')
    ttk.Button(spell_buttons, text='Choose dnd5e system folder', command=lambda: spell_input.set(
        filedialog.askdirectory() or spell_input.get())).pack(side='left')
    ttk.Button(spell_buttons, text='Choose spells pack / system ZIP', command=lambda: spell_input.set(
        filedialog.askopenfilename(filetypes=[('Spells JSON/NeDB or system ZIP', '*.json *.db *.zip')]) or spell_input.get())).pack(side='left')
    ttk.Label(panel, text='New output folder (must not exist)').pack(anchor='w')
    ttk.Entry(panel, textvariable=output).pack(fill='x')
    ttk.Button(panel, text='Choose where to save output', command=lambda: choose_output()).pack(anchor='w', pady=4)
    output_preview = tk.StringVar()
    def preview_output(*_):
        output_preview.set('Folder to create: ' + output.get() if output.get() else 'Folder to create: choose where to save output.')
    output.trace_add('write', preview_output); preview_output()
    ttk.Label(panel, textvariable=output_preview, wraplength=850).pack(anchor='w')
    for label, variable in [('Map folder', map_folder), ('Notes folder', notes_folder)]:
        ttk.Label(panel, text=label).pack(anchor='w')
        ttk.Entry(panel, textvariable=variable).pack(fill='x')
    ttk.Checkbutton(panel, text='Convert PDF handouts into note pages', variable=pdf_pages).pack(anchor='w')
    ttk.Checkbutton(panel, text='Include artwork (FG ART)', variable=include_art, command=lambda: find()).pack(anchor='w')
    ttk.Label(panel, text='Scenes — select one or more (pack/Adventure scope is preserved)').pack(anchor='w')
    scenes = tk.Listbox(panel, selectmode='extended', exportselection=False, height=9)
    scenes.pack(fill='x')
    selection_buttons = ttk.Frame(panel); selection_buttons.pack(fill='x', pady=4)
    ttk.Button(selection_buttons, text='Select all', command=lambda: scenes.selection_set(0, 'end')).pack(side='left')
    ttk.Button(selection_buttons, text='Clear', command=lambda: scenes.selection_clear(0, 'end')).pack(side='left')
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
            except Exception as exc: jobs.put((done, None, (str(exc), traceback.format_exc())))
        threading.Thread(target=worker, daemon=True).start()

    def display(value):
        text.delete('1.0', 'end'); text.insert('1.0', report_text(value))

    def found(report, source):
        rows[:] = populate_scenes(scenes, report); state['source'] = source
        state['source_type'] = report.get('source_type')
        renamed.clear(); grids.clear(); across.clear()
        if rows:
            try: folder = default_folder(rows[0], report.get('package_title'))
            except ValueError as exc:
                folder = ''; messagebox.showerror('Folder name needs attention', str(exc))
            map_folder.set(folder); notes_folder.set(folder)
        status.set(f'{len(rows)} scenes found. Select the scenes to convert, then choose an output folder.')
        display(report)

    def rename_selected(event=None):
        if state['busy']: return
        for index in scenes.curselection():
            row = rows[index]
            value = simpledialog.askstring('Rename map', 'Map name for ' + scene_label(row),
                                           initialvalue=renamed.get(row['key'], row.get('name') or row['id']), parent=app)
            if value is None: continue
            try: value = sanitize_name(value)
            except ValueError as exc:
                messagebox.showerror('Invalid map name', str(exc)); continue
            renamed[row['key']] = value
            scenes.delete(index); scenes.insert(index, scene_label({**row, 'name': value})); scenes.selection_set(index)
    scenes.bind('<Double-Button-1>', rename_selected)
    ttk.Button(selection_buttons, text='Rename selected maps', command=rename_selected).pack(side='left')

    def grid_selected(mode):
        if state['busy']: return
        for index in scenes.curselection():
            row = rows[index]
            if row.get('source_type') != 'fantasy_grounds':
                messagebox.showerror('Fantasy Grounds grid only', 'Foundry grids come from the source scene.'); continue
            if row.get('pixels_per_square'):
                messagebox.showinfo('Stored grid wins', f"This module stores {row['pixels_per_square']:g} pixels per square; it cannot be overridden."); continue
            label = 'Squares across' if mode == 'squares' else 'Pixels per square'
            value = simpledialog.askfloat(label, label + ' for ' + row['name'], minvalue=0.000001, parent=app)
            if value is None: continue
            if not math.isfinite(value) or value <= 0:
                messagebox.showerror('Invalid grid', 'Supply a finite positive number.'); continue
            (across if mode == 'squares' else grids)[row['key']] = value
            (grids if mode == 'squares' else across).pop(row['key'], None)
            row['grid_supplied'] = f'{value:g} {label.lower()} supplied'
            scenes.delete(index); scenes.insert(index, scene_label({**row, 'name': renamed.get(row['key'], row['name'])})); scenes.selection_set(index)
    ttk.Button(selection_buttons, text='Squares across', command=lambda: grid_selected('squares')).pack(side='left')
    ttk.Button(selection_buttons, text='Pixels per square', command=lambda: grid_selected('pixels')).pack(side='left')

    def find():
        source = package.get()
        if not source: messagebox.showerror('Source required', 'Select a package or module first.'); return
        if state['busy']: return
        state['report'] = None; install_button.configure(state='disabled')
        art = include_art.get()
        start(lambda: discover(source, include_art=art) if art else discover(source), lambda report: found(report, source))

    def profiles_pick():
        if state['busy']: return
        chosen = filedialog.askopenfilenames(filetypes=[('Scene profiles', '*.json')])
        if chosen:
            profiles[:] = chosen
            profile_label.set(f'{len(profiles)} existing profiles selected; pinned profile names are used. '
                              'Visible naming fields apply when building without profiles.')

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
        names = {key: value for key, value in renamed.items() if key in selected}
        # Ticked = pages when the PDF renderer is available, else references with a reported loss.
        options = {'pdf': None if pdf_pages.get() else 'references'}
        if spell_input.get().strip():
            options['dnd5e_system'] = spell_input.get().strip()
        if state.get('source_type') == 'fantasy_grounds':
            if any(r['status'] in ('NEEDS_GRID', 'ART') and r['key'] not in grids and r['key'] not in across
                   for r in rows if r['key'] in selected):
                messagebox.showerror('Grid required', 'Set Squares across or Pixels per square for each selected uncalibrated map.'); return
            options.update(include_art=include_art.get(), grid_size={k: v for k, v in grids.items() if k in selected},
                           squares={k: v for k, v in across.items() if k in selected})
        if not controls:
            try:
                plans = plan_names([r for r in rows if r['key'] in selected], map_folder=map_folder.get(),
                                   notes_folder=notes_folder.get(), map_names=names)
            except ValueError as exc:
                messagebox.showerror('Naming conflict or invalid name', str(exc)); return
            options.update(map_folder=map_folder.get(), notes_folder=notes_folder.get(), map_names=names)
            display({'chosen_names': list(plans.values())})
        state['build_source'] = source
        state['output'] = dest; state['report'] = None; install_button.configure(state='disabled')
        start(lambda: convert(source, dest, scene_keys=selected, profiles=controls, **options), built)

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
        try:
            audit = review(packages, target)
            if not audit['ok']:
                conflicts = [row['path'] + ': ' + row.get('detail', row['status']) for row in audit['files']
                             if row['status'] in ('conflict', 'blocked')]
                messagebox.showerror('Installation conflicts — rename or review', '\n'.join(conflicts)); return
        except (OSError, ValueError) as exc:
            messagebox.showerror('Installation review refused', str(exc)); return
        backups = filedialog.askdirectory(title='Select separate existing backup directory')
        if not backups: return
        if not messagebox.askyesno('Review add-only installation',
            f'Install {len(packages)} native packages from {len(report["scenes"])} scene results?\n'
            f'MyAssets: {target}\nBackups: {backups}\n\n'
            'Read the loss report first. Toolkit must stay closed. A full backup is made; conflicts refuse all copying. '
            'Manual UVTT scenes are not installed.\n'
            'Opening notes in the Toolkit can change them; uninstall with --keep-changed later keeps those edits.'): return
        def installed(result):
            display(result)
            text.insert('end', '\n\nBuild loss report (unchanged): ' + str(Path(dest) / 'conversion-report.json')
                        + '\nReopen it any time; the install summary above does not replace it.\n')
            status.set('Added native files. Backup/uninstall receipt shown. No Toolkit validation performed.')
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
                report_error(error[0], error[1], output=output.get())
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
