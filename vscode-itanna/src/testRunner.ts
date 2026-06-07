// ⚡ Itanna Test Runner
// Provides a terminal-based test runner for the electrical package.

import * as vscode from 'vscode';
import * as path from 'path';
import { getPythonPath } from './venv';

/**
 * Run the electrical package test suite in a dedicated terminal.
 */
export async function runEETests(): Promise<void> {
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  if (!workspaceRoot) {
    vscode.window.showErrorMessage('No workspace folder open.');
    return;
  }

  const electricalPath = path.join(workspaceRoot, 'electrical');
  const pythonPath = getPythonPath();

  // Check if the electrical directory exists
  const fs = require('fs');
  if (!fs.existsSync(electricalPath)) {
    vscode.window.showErrorMessage(
      `Electrical package not found at: ${electricalPath}`
    );
    return;
  }

  // Create or reuse a terminal
  const terminals = vscode.window.terminals;
  let terminal = terminals.find(t => t.name === 'Itanna EE Tests');

  if (!terminal) {
    terminal = vscode.window.createTerminal({
      name: 'Itanna EE Tests',
      cwd: electricalPath,
    });
  }

  terminal.show();
  terminal.sendText(`"${pythonPath}" -m pytest tests/ -v --tb=short`);

  vscode.window.setStatusBarMessage('$(testing) Running EE tests...', 3000);
}

/**
 * Run a single test file from the electrical package.
 */
export async function runEESingleTest(testFile: string): Promise<void> {
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  if (!workspaceRoot) return;

  const electricalPath = path.join(workspaceRoot, 'electrical');
  const pythonPath = getPythonPath();

  const terminal = vscode.window.createTerminal({
    name: 'Itanna Single Test',
    cwd: electricalPath,
  });

  terminal.show();
  terminal.sendText(
    `"${pythonPath}" -m pytest tests/${testFile} -v --tb=long`
  );
}
