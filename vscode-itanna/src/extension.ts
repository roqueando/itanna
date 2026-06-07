// ⚡ Itanna for VSCode — Extension Entry Point
// Activates all Itanna commands, views, and integrations.

import * as vscode from 'vscode';
import { registerCommands } from './commands';
import { activateVenv, deactivateVenv } from './venv';
import { WelcomePanel } from './welcome';
import { ItannaTreeDataProvider } from './treeView';
import { ItannaStatusBar } from './status';

let statusBar: ItannaStatusBar;

export function activate(context: vscode.ExtensionContext) {
  console.log('⚡ Itanna for VSCode activating...');

  // ── Status Bar ──────────────────────────────────────────────
  statusBar = new ItannaStatusBar();
  context.subscriptions.push(statusBar);

  // ── Tree Views ──────────────────────────────────────────────
  const toolsProvider = new ItannaTreeDataProvider('tools');
  const notebooksProvider = new ItannaTreeDataProvider('notebooks');

  context.subscriptions.push(
    vscode.window.registerTreeDataProvider('itanna-tools', toolsProvider),
    vscode.window.registerTreeDataProvider('itanna-notebooks', notebooksProvider)
  );

  // ── Commands ────────────────────────────────────────────────
  registerCommands(context);

  // ── Virtual Environment ─────────────────────────────────────
  const config = vscode.workspace.getConfiguration('itanna');
  if (config.get<boolean>('autoActivateVenv', true)) {
    activateVenv().then(() => {
      statusBar.updateVenvStatus(true);
    }).catch(() => {
      statusBar.updateVenvStatus(false);
    });
  }

  // ── Welcome Page on First Open ──────────────────────────────
  if (config.get<boolean>('showWelcomeOnStartup', true)) {
    const hasSeenWelcome = context.globalState.get<boolean>('itanna.hasSeenWelcome', false);
    if (!hasSeenWelcome) {
      setTimeout(() => {
        vscode.commands.executeCommand('itanna.showWelcome');
        context.globalState.update('itanna.hasSeenWelcome', true);
      }, 1000);
    }
  }

  // ── File System Watcher for Templates ───────────────────────
  const templateWatcher = vscode.workspace.createFileSystemWatcher(
    new vscode.RelativePattern(
      vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ?? '',
      'templates-jupyter/*.ipynb'
    )
  );
  templateWatcher.onDidCreate(() => notebooksProvider.refresh());
  templateWatcher.onDidDelete(() => notebooksProvider.refresh());
  context.subscriptions.push(templateWatcher);

  // ── Cleanup ─────────────────────────────────────────────────
  context.subscriptions.push({
    dispose: () => {
      deactivateVenv();
      statusBar.dispose();
    }
  });

  console.log('⚡ Itanna for VSCode activated successfully');
}

export function deactivate() {
  console.log('⚡ Itanna for VSCode deactivated');
}
