// ⚡ Itanna Notebook Templates
// Handles creation of new Jupyter notebooks from template files.

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Known candidate directories for the Itanna project root.
 * Checks common locations relative to HOME, then common project dirs.
 */
function getCandidateRoots(): string[] {
  const home = process.env.HOME || process.env.USERPROFILE || '';
  const candidates: string[] = [];

  // Environment variable
  if (process.env.ITANNA_ROOT) {
    candidates.push(process.env.ITANNA_ROOT);
  }

  // VSCode setting
  const configRoot = vscode.workspace.getConfiguration('itanna').get<string>('projectRoot');
  if (configRoot) {
    candidates.push(configRoot);
  }

  // Common home-relative locations
  candidates.push(
    path.join(home, 'projects', 'itanna'),
    path.join(home, 'itanna'),
    path.join(home, 'src', 'itanna'),
    path.join(home, 'git', 'itanna'),
  );

  // Workspace folders
  const folders = vscode.workspace.workspaceFolders;
  if (folders) {
    for (const folder of folders) {
      candidates.push(folder.uri.fsPath);
      // Parent of workspace folder
      candidates.push(path.resolve(folder.uri.fsPath, '..'));
    }
  }

  return candidates;
}

/**
 * Find the Itanna project root directory.
 *
 * Tries, in order:
 * 1. ITANNA_ROOT environment variable
 * 2. VSCode "itanna.projectRoot" setting
 * 3. Known common paths (projects/itanna, ~/itanna, etc.)
 * 4. Walk up from workspace folders
 * 5. Walk up from the extension install directory (for F5 dev mode)
 *
 * A directory is considered the itanna root if it contains:
 *   - pyproject.toml  AND
 *   - templates-jupyter/  AND
 *   - electrical/
 */
function isValidItannaRoot(dir: string): boolean {
  try {
    return (
      fs.existsSync(path.join(dir, 'pyproject.toml')) &&
      fs.existsSync(path.join(dir, 'templates-jupyter')) &&
      fs.existsSync(path.join(dir, 'electrical'))
    );
  } catch {
    return false;
  }
}

let _cachedRoot: string | undefined = undefined;

/**
 * Find the Itanna project root with caching.
 */
export function findItannaRoot(): string | undefined {
  if (_cachedRoot) return _cachedRoot;

  // Check all candidates
  for (const candidate of getCandidateRoots()) {
    if (candidate && isValidItannaRoot(candidate)) {
      _cachedRoot = candidate;
      return _cachedRoot;
    }
  }

  // Walk up from extension install dir (for F5 development mode)
  const extDir = __dirname;
  for (let d = path.resolve(extDir, '..'); d !== path.resolve(d, '..'); d = path.resolve(d, '..')) {
    if (isValidItannaRoot(d)) {
      _cachedRoot = d;
      return _cachedRoot;
    }
    if (d === '/') break;
  }

  return undefined;
}

/**
 * Reset the cached root (e.g., after settings change).
 */
export function resetItannaRoot(): void {
  _cachedRoot = undefined;
}

/**
 * Get the path to the templates-jupyter directory.
 */
export function getTemplatePath(itannaRoot: string): string {
  const templatesDir = path.join(itannaRoot, 'templates-jupyter');
  if (!fs.existsSync(templatesDir)) {
    throw new Error(`Templates directory not found at: ${templatesDir}`);
  }
  return templatesDir;
}

/**
 * Get the user notebooks directory, creating it if needed.
 */
export function getUserNotebooksPath(): string {
  const homeDir = process.env.HOME || process.env.USERPROFILE || '';
  const notebooksDir = path.join(homeDir, '.itanna', 'notebooks');
  if (!fs.existsSync(notebooksDir)) {
    fs.mkdirSync(notebooksDir, { recursive: true });
  }
  return notebooksDir;
}

/**
 * Create a new Jupyter notebook from a template file.
 *
 * @param context The extension context (for state/display)
 * @param templateName The template file name (e.g., "template-ee.ipynb")
 */
export async function createNotebookFromTemplate(
  context: vscode.ExtensionContext,
  templateName: string
): Promise<void> {
  const itannaRoot = findItannaRoot();
  if (!itannaRoot) {
    vscode.window.showErrorMessage(
      'Itanna project root not found. Open the itanna workspace folder, ' +
      'set the ITANNA_ROOT environment variable, or run from the itanna project directory.'
    );
    return;
  }

  let templatesDir: string;
  try {
    templatesDir = getTemplatePath(itannaRoot);
  } catch (e) {
    vscode.window.showErrorMessage(
      `Templates directory not found. Expected at: ${path.join(itannaRoot, 'templates-jupyter')}`
    );
    return;
  }

  const templatePath = path.join(templatesDir, templateName);

  if (!fs.existsSync(templatePath)) {
    vscode.window.showErrorMessage(
      `Template not found: ${templatePath}. ` +
      `Make sure templates-jupyter/ exists with notebook templates.`
    );
    return;
  }

  // Ask user for a name, with sensible default
  const defaultName = templateName.replace('.ipynb', '') + '-' + new Date().toISOString().slice(0, 10);
  const name = await vscode.window.showInputBox({
    prompt: `Save notebook as (in ~/.itanna/notebooks/)`,
    placeHolder: defaultName,
    value: defaultName,
    validateInput: (value) => {
      if (!value.trim()) return 'Name cannot be empty';
      if (!/^[a-zA-Z0-9_-]+$/.test(value)) return 'Use only letters, numbers, hyphens, and underscores';
      return null;
    }
  });

  if (!name) return; // User cancelled

  const notebooksDir = getUserNotebooksPath();
  const targetPath = path.join(notebooksDir, `${name}.ipynb`);

  if (fs.existsSync(targetPath)) {
    const overwrite = await vscode.window.showWarningMessage(
      `Notebook "${name}.ipynb" already exists. Overwrite?`,
      { modal: true },
      'Overwrite',
      'Cancel'
    );
    if (overwrite !== 'Overwrite') return;
  }

  // Copy the template
  try {
    const content = fs.readFileSync(templatePath, 'utf-8');
    fs.writeFileSync(targetPath, content, 'utf-8');
  } catch (err) {
    vscode.window.showErrorMessage(`Failed to create notebook: ${err}`);
    return;
  }

  // Open the new notebook using VSCode's built-in notebook opener
  await vscode.commands.executeCommand('vscode.open', vscode.Uri.file(targetPath));

  vscode.window.showInformationMessage(`📓 Created notebook: ${name}.ipynb`);
}
