// ⚡ Itanna Status Bar Items
// Shows venv status, Python version, and quick actions in the status bar.

import * as vscode from 'vscode';
import { isVenvActive, getPythonPath } from './venv';
import { execSync } from 'child_process';

export class ItannaStatusBar {
  private readonly _venvItem: vscode.StatusBarItem;
  private readonly _pythonItem: vscode.StatusBarItem;
  private readonly _disposables: vscode.Disposable[] = [];

  constructor() {
    // ── Virtual Environment Status ────────────────────────────
    this._venvItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Left,
      100
    );
    this._venvItem.command = 'itanna.activateVenv';
    this._venvItem.tooltip = 'Click to activate Itanna Python virtual environment';
    this._venvItem.text = '$(gear) Itanna...';
    this._venvItem.show();
    this._disposables.push(this._venvItem);

    // ── Python Version ────────────────────────────────────────
    this._pythonItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      50
    );
    this._pythonItem.tooltip = 'Python version';
    this._pythonItem.show();
    this._disposables.push(this._pythonItem);

    // Update on activation
    this._updateStatus();

    // Listen for configuration changes
    this._disposables.push(
      vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('python.defaultInterpreterPath') ||
            e.affectsConfiguration('itanna.autoActivateVenv')) {
          this._updateStatus();
        }
      })
    );
  }

  /**
   * Update venv status indicator.
   */
  public updateVenvStatus(active: boolean): void {
    if (active) {
      this._venvItem.text = '$(check) Itanna Venv';
      this._venvItem.backgroundColor = new vscode.ThemeColor(
        'statusBarItem.prominentBackground'
      );
      this._venvItem.tooltip = 'Itanna Python venv is active. Click to re-activate.';
    } else {
      this._venvItem.text = '$(warning) Itanna Venv';
      this._venvItem.backgroundColor = undefined;
      this._venvItem.tooltip = 'Itanna venv not active. Click to activate.';
    }

    // Also update Python version display
    this._updatePythonVersion();
  }

  /**
   * Update all status indicators.
   */
  private _updateStatus(): void {
    const active = isVenvActive();
    this.updateVenvStatus(active);
  }

  /**
   * Update the Python version in the status bar.
   */
  private _updatePythonVersion(): void {
    try {
      const pythonPath = getPythonPath();
      const version = execSync(`"${pythonPath}" --version 2>&1`, { encoding: 'utf-8' }).trim();
      const short = version.replace('Python ', '');
      this._pythonItem.text = `$(symbol-numeric) Python ${short}`;
    } catch {
      this._pythonItem.text = '$(warning) Python N/A';
    }
  }

  public dispose(): void {
    this._disposables.forEach(d => d.dispose());
  }
}
