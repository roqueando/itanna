// ⚡ Itanna Commands — All command registrations

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { activateVenv } from './venv';
import { WelcomePanel } from './welcome';
import { findItannaRoot, getTemplatePath, createNotebookFromTemplate, resetItannaRoot } from './templates';
import { insertBuckSnippet, insertExecutableSnippet } from './snippets';

export function registerCommands(context: vscode.ExtensionContext) {
  const itannaRoot = findItannaRoot();
  const workspaceRoot = getWorkspaceRoot();

  // ── Welcome Page ───────────────────────────────────────────
  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.showWelcome', () => {
      WelcomePanel.createOrShow(context.extensionUri);
    })
  );

  // ── New Notebooks from Templates ───────────────────────────
  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.newEENotebook', async () => {
      await createNotebookFromTemplate(context, 'template-ee.ipynb');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.newBuckCalculatorNotebook', async () => {
      await createNotebookFromTemplate(context, 'buck-calculator.ipynb');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.newExecutableDemoNotebook', async () => {
      await createNotebookFromTemplate(context, 'hello-executable.ipynb');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.openTemplateNotebook', async () => {
      const root = findItannaRoot();
      if (!root) {
        vscode.window.showErrorMessage('Itanna project root not found.');
        return;
      }
      let templatesDir: string;
      try {
        templatesDir = getTemplatePath(root);
      } catch {
        vscode.window.showErrorMessage(`Templates directory not found in itanna project: ${path.join(root, 'templates-jupyter')}`);
        return;
      }
      const files = fs.readdirSync(templatesDir)
        .filter(f => f.endsWith('.ipynb'))
        .map(f => ({
          label: f.replace('.ipynb', ''),
          description: f,
          filePath: path.join(templatesDir, f)
        }));

      if (files.length === 0) {
        vscode.window.showInformationMessage('No notebook templates found.');
        return;
      }

      const picked = await vscode.window.showQuickPick(files, {
        placeHolder: 'Select a notebook template to open'
      });

      if (picked) {
        await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(picked.filePath));
      }
    })
  );

  // ── Insert EE Snippets ──────────────────────────────────────
  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.insertBuckSnippet', () => {
      const editor = vscode.window.activeTextEditor;
      if (editor) {
        insertBuckSnippet(editor);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.insertExecutableSnippet', () => {
      const editor = vscode.window.activeTextEditor;
      if (editor) {
        insertExecutableSnippet(editor);
      }
    })
  );

  // ── Virtual Environment ─────────────────────────────────────
  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.activateVenv', async () => {
      const success = await activateVenv(true);
      vscode.window.showInformationMessage(
        success ? '✅ Itanna Python environment activated' : '❌ Failed to activate Python environment'
      );
    })
  );

  // ── Run EE Tests ────────────────────────────────────────────
  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.runEETests', async () => {
      const root = findItannaRoot();
      if (!root) {
        vscode.window.showErrorMessage('Itanna project root not found.');
        return;
      }
      const electricalPath = path.join(root, 'electrical');
      if (!fs.existsSync(electricalPath)) {
        vscode.window.showErrorMessage('Electrical package not found in itanna project.');
        return;
      }

      const terminal = vscode.window.createTerminal({
        name: 'Itanna EE Tests',
        cwd: electricalPath
      });
      terminal.show();
      terminal.sendText('python3 -m pytest tests/ -v');
    })
  );

  // ── Open EE Package ─────────────────────────────────────────
  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.openEEPackage', async () => {
      const root = findItannaRoot();
      if (!root) {
        vscode.window.showErrorMessage('Itanna project root not found.');
        return;
      }
      const electricalPath = path.join(root, 'electrical', 'electrical');
      if (!fs.existsSync(electricalPath)) {
        vscode.window.showErrorMessage('Electrical package directory not found.');
        return;
      }
      const uri = vscode.Uri.file(electricalPath);
      await vscode.commands.executeCommand('revealInExplorer', uri);
    })
  );

  // ── Rust / Cargo Tasks ──────────────────────────────────────
  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.cargoCheck', () => {
      runTask('Itanna: Cargo Check');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.cargoRun', () => {
      runTask('Itanna: Cargo Run');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.cargoTest', () => {
      runTask('Itanna: Cargo Test');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.cargoNewProject', async () => {
      const name = await vscode.window.showInputBox({
        prompt: 'Enter the Cargo project name',
        placeHolder: 'itanna-ee-crate',
        validateInput: (value) => {
          if (!/^[a-zA-Z_][a-zA-Z0-9_-]*$/.test(value)) {
            return 'Invalid Rust crate name';
          }
          return null;
        }
      });
      if (name) {
        const terminal = vscode.window.createTerminal({
          name: 'Itanna Cargo New',
          cwd: workspaceRoot
        });
        terminal.show();
        terminal.sendText(`cargo new --bin ${name}`);
      }
    })
  );

  // ── CMake Build ─────────────────────────────────────────────
  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.cmakeBuild', () => {
      runTask('Itanna: CMake Build');
    })
  );

  // ── Set Itanna Root ─────────────────────────────────────────
  context.subscriptions.push(
    vscode.commands.registerCommand('itanna.setItannaRoot', async () => {
      const current = findItannaRoot() || '';
      const picked = await vscode.window.showOpenDialog({
        canSelectFiles: false,
        canSelectFolders: true,
        canSelectMany: false,
        defaultUri: current ? vscode.Uri.file(current) : undefined,
        openLabel: 'Select Itanna Project Root',
        title: 'Select the Itanna project root directory (contains pyproject.toml, templates-jupyter, electrical/)'
      });
      if (picked && picked.length > 0) {
        const selectedPath = picked[0].fsPath;
        const config = vscode.workspace.getConfiguration('itanna');
        await config.update('projectRoot', selectedPath, vscode.ConfigurationTarget.Global);
        resetItannaRoot();
        vscode.window.showInformationMessage(`✅ Itanna root set to: ${selectedPath}`);
      }
    })
  );
}

function getWorkspaceRoot(): string | undefined {
  return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
}

async function runTask(taskLabel: string) {
  try {
    const tasks = await vscode.tasks.fetchTasks();
    const task = tasks.find(t => t.name === taskLabel);
    if (task) {
      await vscode.tasks.executeTask(task);
    } else {
      throw new Error(`Task "${taskLabel}" not found. Make sure .vscode/tasks.json is configured.`);
    }
  } catch (err) {
    vscode.window.showErrorMessage(`Failed to run task: ${(err as Error).message}`);
  }
}
