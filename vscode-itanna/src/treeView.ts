// ⚡ Itanna Tree View Providers
// Custom sidebar views showing EE tools and available notebook templates.

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

type ViewType = 'tools' | 'notebooks';

interface ItannaTreeItem {
  label: string;
  description?: string;
  icon?: string;
  command?: string;
  tooltip?: string;
}

/**
 * Tree data provider for Itanna sidebar views.
 */
export class ItannaTreeDataProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<vscode.TreeItem | undefined | null> =
    new vscode.EventEmitter<vscode.TreeItem | undefined | null>();
  readonly onDidChangeTreeData: vscode.Event<vscode.TreeItem | undefined | null> =
    this._onDidChangeTreeData.event;

  constructor(private viewType: ViewType) {}

  refresh(): void {
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: vscode.TreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: vscode.TreeItem): Thenable<vscode.TreeItem[]> {
    if (element) {
      return Promise.resolve([]);
    }

    if (this.viewType === 'tools') {
      return Promise.resolve(this._getToolsItems());
    } else {
      return Promise.resolve(this._getNotebookItems());
    }
  }

  private _getToolsItems(): vscode.TreeItem[] {
    const items: ItannaTreeItem[] = [
      {
        label: '📓 New EE Notebook',
        command: 'itanna.newEENotebook',
        tooltip: 'Create a new EE notebook from template'
      },
      {
        label: '⚡ Buck Calculator',
        command: 'itanna.newBuckCalculatorNotebook',
        tooltip: 'Open the buck converter design notebook'
      },
      {
        label: '📦 Executable Builder',
        command: 'itanna.newExecutableDemoNotebook',
        tooltip: 'Build a standalone executable from Python'
      },
      {
        label: '🧪 Run EE Tests',
        command: 'itanna.runEETests',
        tooltip: 'Run the electrical package tests'
      },
      {
        label: '📂 Open EE Package',
        command: 'itanna.openEEPackage',
        tooltip: 'Browse the electrical Python package'
      },
      {
        label: '🔌 Activate Venv',
        command: 'itanna.activateVenv',
        tooltip: 'Activate the Python virtual environment'
      },
      {
        label: '🏠 Welcome Page',
        command: 'itanna.showWelcome',
        tooltip: 'Show the welcome page'
      },
    ];

    return items.map(item => {
      const treeItem = new vscode.TreeItem(
        item.label,
        vscode.TreeItemCollapsibleState.None
      );
      treeItem.tooltip = item.tooltip;
      treeItem.command = {
        command: item.command!,
        title: item.label,
      };
      return treeItem;
    });
  }

  private _getNotebookItems(): vscode.TreeItem[] {
    const items: vscode.TreeItem[] = [];
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

    // Template notebooks
    if (workspaceRoot) {
      const templatesDir = path.join(workspaceRoot, 'templates-jupyter');
      if (fs.existsSync(templatesDir)) {
        const templateFiles = fs.readdirSync(templatesDir)
          .filter(f => f.endsWith('.ipynb'))
          .sort();

        if (templateFiles.length > 0) {
          const templatesHeader = new vscode.TreeItem(
            '📁 Templates',
            vscode.TreeItemCollapsibleState.Expanded
          );
          templatesHeader.description = `${templateFiles.length} files`;
          items.push(templatesHeader);

          templateFiles.forEach(file => {
            const childItem = new vscode.TreeItem(
              file.replace('.ipynb', ''),
              vscode.TreeItemCollapsibleState.None
            );
            childItem.description = 'template';
            childItem.tooltip = path.join(templatesDir, file);
            childItem.command = {
              command: 'vscode.open',
              title: 'Open Template',
              arguments: [vscode.Uri.file(path.join(templatesDir, file))]
            };
            childItem.iconPath = new vscode.ThemeIcon('notebook');
            items.push(childItem);
          });
        }
      }

      // User notebooks
      const homeDir = process.env.HOME || process.env.USERPROFILE || '';
      const userNotebooksDir = path.join(homeDir, '.itanna', 'notebooks');
      if (fs.existsSync(userNotebooksDir)) {
        const userFiles = fs.readdirSync(userNotebooksDir)
          .filter(f => f.endsWith('.ipynb'))
          .sort();

        if (userFiles.length > 0) {
          const userHeader = new vscode.TreeItem(
            '📝 My Notebooks',
            vscode.TreeItemCollapsibleState.Expanded
          );
          userHeader.description = `${userFiles.length} notebooks`;
          items.push(userHeader);

          userFiles.forEach(file => {
            const childItem = new vscode.TreeItem(
              file.replace('.ipynb', ''),
              vscode.TreeItemCollapsibleState.None
            );
            childItem.tooltip = path.join(userNotebooksDir, file);
            childItem.command = {
              command: 'vscode.open',
              title: 'Open Notebook',
              arguments: [vscode.Uri.file(path.join(userNotebooksDir, file))]
            };
            childItem.iconPath = new vscode.ThemeIcon('notebook');
            items.push(childItem);
          });
        }
      }
    }

    if (items.length === 0) {
      const emptyItem = new vscode.TreeItem(
        'No notebooks found',
        vscode.TreeItemCollapsibleState.None
      );
      emptyItem.description = 'Create one with Ctrl+Alt+N';
      items.push(emptyItem);
    }

    return items;
  }
}
