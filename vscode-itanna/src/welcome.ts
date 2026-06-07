// ⚡ Itanna Welcome Page — Webview Panel
// Displays a welcome/landing page with keybindings, environment status, and links.

import * as vscode from 'vscode';
import { isVenvActive, getPythonPath, findVenvPath } from './venv';
import { execSync } from 'child_process';
import * as path from 'path';

export class WelcomePanel {
  public static currentPanel: WelcomePanel | undefined;

  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;
  private _disposables: vscode.Disposable[] = [];

  private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    this._panel.webview.html = this._getHtmlContent();
    this._panel.webview.onDidReceiveMessage(
      this._handleMessage,
      null,
      this._disposables
    );
  }

  public static createOrShow(extensionUri: vscode.Uri) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    if (WelcomePanel.currentPanel) {
      WelcomePanel.currentPanel._panel.reveal(column);
      WelcomePanel.currentPanel._refresh();
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      'itannaWelcome',
      '⚡ Itanna — Welcome',
      column ?? vscode.ViewColumn.One,
      {
        enableScripts: true,
        localResourceRoots: [
          vscode.Uri.joinPath(extensionUri, 'resources', 'welcome')
        ]
      }
    );

    WelcomePanel.currentPanel = new WelcomePanel(panel, extensionUri);
  }

  public dispose() {
    WelcomePanel.currentPanel = undefined;
    this._panel.dispose();
    while (this._disposables.length) {
      const d = this._disposables.pop();
      if (d) d.dispose();
    }
  }

  private _refresh() {
    this._panel.webview.html = this._getHtmlContent();
  }

  private _handleMessage(message: any) {
    switch (message.command) {
      case 'newNotebook':
        vscode.commands.executeCommand('itanna.newEENotebook');
        return;
      case 'buckCalculator':
        vscode.commands.executeCommand('itanna.newBuckCalculatorNotebook');
        return;
      case 'executableBuilder':
        vscode.commands.executeCommand('itanna.newExecutableDemoNotebook');
        return;
      case 'runTests':
        vscode.commands.executeCommand('itanna.runEETests');
        return;
      case 'openEEPackage':
        vscode.commands.executeCommand('itanna.openEEPackage');
        return;
      case 'activateVenv':
        vscode.commands.executeCommand('itanna.activateVenv');
        return;
      case 'openREADME':
        vscode.commands.executeCommand('markdown.showPreviewToSide',
          vscode.Uri.file(
            path.join(vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ?? '', 'README.org')
          )
        );
        return;
    }
  }

  private _getHtmlContent(): string {
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ?? '';
    const venvActive = isVenvActive();
    const pythonPath = getPythonPath();

    // Gather environment info
    let pythonVersion = 'N/A';
    let numpyStatus = '❌ Not installed';
    let scipyStatus = '❌ Not installed';
    let matplotlibStatus = '❌ Not installed';
    let nuitkaStatus = '❌ Not installed';

    try {
      pythonVersion = execSync(`"${pythonPath}" --version 2>&1`, { encoding: 'utf-8' }).trim();
    } catch { /* ignore */ }

    try {
      execSync(`"${pythonPath}" -c "import numpy" 2>&1`, { encoding: 'utf-8' });
      const ver = execSync(`"${pythonPath}" -c "import numpy; print(numpy.__version__)" 2>&1`, { encoding: 'utf-8' }).trim();
      numpyStatus = `✅ ${ver}`;
    } catch { /* ignore */ }

    try {
      execSync(`"${pythonPath}" -c "import scipy" 2>&1`, { encoding: 'utf-8' });
      const ver = execSync(`"${pythonPath}" -c "import scipy; print(scipy.__version__)" 2>&1`, { encoding: 'utf-8' }).trim();
      scipyStatus = `✅ ${ver}`;
    } catch { /* ignore */ }

    try {
      execSync(`"${pythonPath}" -c "import matplotlib" 2>&1`, { encoding: 'utf-8' });
      const ver = execSync(`"${pythonPath}" -c "import matplotlib; print(matplotlib.__version__)" 2>&1`, { encoding: 'utf-8' }).trim();
      matplotlibStatus = `✅ ${ver}`;
    } catch { /* ignore */ }

    try {
      execSync(`"${pythonPath}" -c "import nuitka" 2>&1`, { encoding: 'utf-8' });
      nuitkaStatus = '✅ Installed';
    } catch { /* ignore */ }

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>⚡ Itanna — Welcome</title>
  <style>
    :root {
      --bg: #fdf6e3;
      --fg: #657b83;
      --head: #073642;
      --accent: #268bd2;
      --green: #859900;
      --red: #dc322f;
      --border: #eee8d5;
      --card-bg: #fff9e6;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Ubuntu', sans-serif;
      background: var(--bg);
      color: var(--fg);
      max-width: 900px;
      margin: 0 auto;
      padding: 2rem;
      line-height: 1.6;
    }
    h1 { color: var(--head); font-size: 1.8rem; margin-bottom: 0.3rem; }
    h1 .bolt { color: #b58900; }
    h2 { color: var(--head); font-size: 1.3rem; border-bottom: 2px solid var(--border);
         padding-bottom: 0.3rem; margin-top: 2rem; }
    h3 { color: var(--head); font-size: 1.1rem; }
    .subtitle { font-size: 1rem; color: var(--fg); margin-bottom: 1.5rem; }
    .button-bar { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0; }
    .btn {
      display: inline-flex; align-items: center; gap: 0.4rem;
      padding: 0.5rem 1rem; border-radius: 6px; border: 1px solid var(--border);
      background: var(--card-bg); color: var(--head); cursor: pointer;
      font-size: 0.9rem; text-decoration: none; transition: all 0.15s;
    }
    .btn:hover { background: #f0e8d5; border-color: var(--accent); }
    .btn-primary { background: var(--accent); color: white; border-color: var(--accent); }
    .btn-primary:hover { background: #1a7bc4; }
    .env-grid { display: grid; grid-template-columns: auto 1fr; gap: 0.3rem 1rem;
                background: var(--card-bg); border: 1px solid var(--border);
                border-radius: 8px; padding: 1rem; margin: 0.5rem 0; font-size: 0.9rem; }
    .env-grid .label { font-weight: 600; color: var(--head); }
    .key-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin: 0.5rem 0; }
    .key-table th, .key-table td { padding: 0.3rem 0.6rem; text-align: left;
                                    border-bottom: 1px solid var(--border); }
    .key-table th { font-weight: 600; color: var(--head); background: var(--card-bg); }
    .key-table code { background: #eee8d5; padding: 0.1rem 0.3rem; border-radius: 3px;
                      font-family: 'Fira Code', 'JetBrains Mono', monospace; font-size: 0.8rem; }
    .section-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
    @media (max-width: 600px) { .section-grid { grid-template-columns: 1fr; } }
    .status-ok { color: var(--green); }
    .status-err { color: var(--red); }
    footer { margin-top: 2rem; font-size: 0.8rem; color: #93a1a1;
             text-align: center; border-top: 1px solid var(--border); padding-top: 1rem; }
  </style>
</head>
<body>
  <h1><span class="bolt">⚡</span> Itanna — Electrical Engineering for VSCode</h1>
  <div class="subtitle">Python · Julia · C/C++ · Rust · Jupyter Notebooks</div>

  <div class="button-bar">
    <button class="btn btn-primary" onclick="send('newNotebook')">📓 New EE Notebook</button>
    <button class="btn" onclick="send('buckCalculator')">⚡ Buck Calculator</button>
    <button class="btn" onclick="send('executableBuilder')">📦 Executable Builder</button>
    <button class="btn" onclick="send('runTests')">🧪 Run EE Tests</button>
    <button class="btn" onclick="send('activateVenv')">🔌 Activate Venv</button>
    <button class="btn" onclick="send('openREADME')">📖 README</button>
  </div>

  <h2>🔧 Environment</h2>
  <div class="env-grid">
    <span class="label">Workspace:</span><span>${workspaceRoot || 'N/A'}</span>
    <span class="label">Version:</span><span>0.1.0</span>
    <span class="label">Python:</span><span>${pythonVersion || 'N/A'}</span>
    <span class="label">Venv Active:</span><span class="${venvActive ? 'status-ok' : 'status-err'}">${venvActive ? '✅ Yes' : '❌ No'}</span>
    <span class="label">NumPy:</span><span>${numpyStatus}</span>
    <span class="label">SciPy:</span><span>${scipyStatus}</span>
    <span class="label">Matplotlib:</span><span>${matplotlibStatus}</span>
    <span class="label">Nuitka:</span><span>${nuitkaStatus}</span>
  </div>

  <h2>🎯 Quick Start</h2>
  <div class="section-grid">
    <div>
      <h3>📓 Notebooks</h3>
      <table class="key-table">
        <tr><th>Action</th><th>Command / Keybinding</th></tr>
        <tr><td>New EE Notebook</td><td><code>Ctrl+Alt+N</code></td></tr>
        <tr><td>Insert Buck Snippet</td><td><code>Ctrl+Alt+B</code> (Python)</td></tr>
        <tr><td>Insert Exec Builder</td><td><code>Ctrl+Alt+X</code> (Python)</td></tr>
        <tr><td>Run EE Tests</td><td><code>Ctrl+Alt+T</code></td></tr>
        <tr><td>Show Welcome</td><td><code>Ctrl+Alt+W</code></td></tr>
      </table>
    </div>
    <div>
      <h3>🦀 Rust / Cargo</h3>
      <table class="key-table">
        <tr><th>Action</th><th>Command</th></tr>
        <tr><td>Cargo Check</td><td><code>Itanna: Cargo Check</code></td></tr>
        <tr><td>Cargo Run</td><td><code>Itanna: Cargo Run</code></td></tr>
        <tr><td>Cargo Test</td><td><code>Itanna: Cargo Test</code></td></tr>
        <tr><td>New Cargo Project</td><td><code>Itanna: New Cargo Project</code></td></tr>
      </table>
      <h3>🔨 C/C++ / CMake</h3>
      <table class="key-table">
        <tr><th>Action</th><th>Command</th></tr>
        <tr><td>CMake Build</td><td><code>Itanna: CMake Build</code></td></tr>
      </table>
    </div>
  </div>

  <h2>📚 Templates</h2>
  <p>Open any template notebook from the command palette (<code>Itanna: Open Template Notebook...</code>) or via the sidebar.</p>
  <ul>
    <li><strong>template-ee.ipynb</strong> — Blank EE notebook with Python, Julia, and plotting cells</li>
    <li><strong>buck-calculator.ipynb</strong> — Buck converter design walkthrough</li>
    <li><strong>hello-executable.ipynb</strong> — Function → standalone app with Nuitka</li>
  </ul>

  <h2>💡 Quick Reference</h2>
  <table class="key-table">
    <tr><th>Prefix</th><th>Key</th><th>Action</th></tr>
    <tr><td><code>Ctrl+Alt</code></td><td><code>N</code></td><td>New EE Notebook</td></tr>
    <tr><td><code>Ctrl+Alt</code></td><td><code>B</code></td><td>Insert Buck Calculator snippet</td></tr>
    <tr><td><code>Ctrl+Alt</code></td><td><code>X</code></td><td>Insert Executable Builder snippet</td></tr>
    <tr><td><code>Ctrl+Alt</code></td><td><code>T</code></td><td>Run EE Tests</td></tr>
    <tr><td><code>Ctrl+Alt</code></td><td><code>W</code></td><td>Show Welcome page</td></tr>
    <tr><td><code>Ctrl+Shift+Enter</code></td><td></td><td>Run Jupyter cell</td></tr>
  </table>

  <footer>
    ⚡ Itanna v0.1.0 — Based on the <a href="https://github.com/roqueando/itanna">Itanna Emacs Distribution</a>
    <br>
    Happy engineering!
  </footer>

  <script>
    const vscode = acquireVsCodeApi();
    function send(command) {
      vscode.postMessage({ command });
    }
  </script>
</body>
</html>`;
  }
}
