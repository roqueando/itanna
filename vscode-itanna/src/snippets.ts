// ⚡ Itanna Code Snippets
// Programmatic snippet insertion for EE tools.

import * as vscode from 'vscode';

/**
 * Insert a buck converter calculator Python code block into the active editor.
 */
export function insertBuckSnippet(editor: vscode.TextEditor): void {
  const snippet = new vscode.SnippetString();

  snippet.appendText('from electrical.converter.buck import design_buck\n');
  snippet.appendText('\n');
  snippet.appendText('# ── Buck converter design parameters ──\n');
  snippet.appendText(`vin    = ${12}      # Input voltage (V)\n`);
  snippet.appendText(`vout   = ${3.3}     # Output voltage (V)\n`);
  snippet.appendText(`iout   = ${2.0}     # Output current (A)\n`);
  snippet.appendText(`fsw    = ${300e3} # Switching frequency (Hz)\n`);
  snippet.appendText(`vripple = ${0.01} # Output voltage ripple (V)\n`);
  snippet.appendText('\n');
  snippet.appendText('# ── Run design calculation ──\n');
  snippet.appendText('results = design_buck(\n');
  snippet.appendText('    vin=vin, vout=vout, iout=iout,\n');
  snippet.appendText('    fsw=fsw, vripple=vripple,\n');
  snippet.appendText('    il_ripple_pct=0.30,\n');
  snippet.appendText(')\n');
  snippet.appendText('\n');
  snippet.appendText('# ── Pretty-print results ──\n');
  snippet.appendText('print("─" * 50)\n');
  snippet.appendText('print("  BUCK CONVERTER — Component Selection")\n');
  snippet.appendText('print("─" * 50)\n');
  snippet.appendText('for k, v in results.items():\n');
  snippet.appendText('    if isinstance(v, float):\n');
  snippet.appendText('        print(f"  {k:25s}: {v:.4e}")\n');
  snippet.appendText('    else:\n');
  snippet.appendText('        print(f"  {k:25s}: {v}")\n');
  snippet.appendText('print("─" * 50)\n');

  editor.insertSnippet(snippet);
}

/**
 * Insert an executable builder Python code block into the active editor.
 */
export function insertExecutableSnippet(editor: vscode.TextEditor): void {
  const snippet = new vscode.SnippetString();

  snippet.appendText('from electrical.executable.builder import build_app, tkinter_template\n');
  snippet.appendText('\n');
  snippet.appendText('# ── Define your application logic ──\n');
  snippet.appendText('def my_calculator():\n');
  snippet.appendText("    \"\"\"My EE calculator app\"\"\"\n");
  snippet.appendText('    import tkinter as tk\n');
  snippet.appendText('    from tkinter import ttk\n');
  snippet.appendText('\n');
  snippet.appendText('    root = tk.Tk()\n');
  snippet.appendText('    root.title("EE Calculator")\n');
  snippet.appendText('\n');
  snippet.appendText('    frame = ttk.Frame(root, padding="20")\n');
  snippet.appendText('    frame.pack(fill="both", expand=True)\n');
  snippet.appendText('    ttk.Label(frame, text="Hello from Itanna!",\n');
  snippet.appendText('             font=("Helvetica", 16)).pack()\n');
  snippet.appendText('    ttk.Button(frame, text="Quit",\n');
  snippet.appendText('              command=root.destroy).pack(pady=10)\n');
  snippet.appendText('\n');
  snippet.appendText('    root.mainloop()\n');
  snippet.appendText('\n');
  snippet.appendText('# ── Build standalone executable (requires Nuitka) ──\n');
  snippet.appendText('# build_app(\n');
  snippet.appendText('#     func=my_calculator,\n');
  snippet.appendText('#     name="ee-calculator",\n');
  snippet.appendText('#     gui="tkinter",\n');
  snippet.appendText('#     output_dir="~/Desktop/"\n');
  snippet.appendText('# )\n');
  snippet.appendText('\n');
  snippet.appendText('# Or use the template-based approach:\n');
  snippet.appendText('# source = tkinter_template(\n');
  snippet.appendText('#     title="EE Calculator",\n');
  snippet.appendText('#     width=500,\n');
  snippet.appendText('#     height=400,\n');
  snippet.appendText('#     body=""" ... tkinter code ... """\n');
  snippet.appendText('# )\n');

  editor.insertSnippet(snippet);
}
