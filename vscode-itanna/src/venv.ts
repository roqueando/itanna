// ⚡ Itanna Virtual Environment Activation
// Detects and activates the Poetry-managed Python virtual environment
// for the Itanna workspace, updating PATH and environment variables.

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { execSync, exec } from 'child_process';

let venvActivated = false;

/**
 * Find the Itanna VSCode virtual environment path.
 *
 * Priority:
 * 1. VIRTUAL_ENV environment variable
 * 2. `~/.itanna/.venv/` (dedicated VSCode environment)
 * 3. `.venv/` inside workspace root
 * 4. Poetry's cache directory
 *
 * The dedicated VSCode venv at `~/.itanna/.venv` is preferred because:
 * - It's independent of the Emacs/org-babel venv
 * - It persists regardless of which directory VSCode is opened in
 * - It's managed by the VSCode extension install script
 */
export async function findVenvPath(workspaceRoot: string): Promise<string | null> {
  // 1. Already activated in shell
  const envVar = process.env.VIRTUAL_ENV;
  if (envVar && fs.existsSync(envVar)) {
    return envVar;
  }

  // 2. Dedicated VSCode venv at ~/.itanna/.venv (highest priority for VSCode)
  const home = process.env.HOME || process.env.USERPROFILE || '';
  const itannaDir = path.join(home, '.itanna');
  const itannaVenv = path.join(itannaDir, '.venv');
  const itannaPython = path.join(itannaVenv, 'bin', 'python');
  if (fs.existsSync(itannaPython)) {
    return itannaVenv;
  }

  // 3. In-project venv (shared with Emacs)
  const inProjectVenv = path.join(workspaceRoot, '.venv');
  const inProjectPython = path.join(inProjectVenv, 'bin', 'python');
  if (fs.existsSync(inProjectPython)) {
    return inProjectVenv;
  }

  // 4. Poetry cache (async)
  try {
    const poetryPath = await execAsync('poetry', ['env', 'info', '--path'], { cwd: workspaceRoot });
    const cachePath = poetryPath.trim();
    if (cachePath && fs.existsSync(cachePath)) {
      return cachePath;
    }
  } catch {
    // poetry not available or not configured
  }

  return null;
}

/**
 * Ensure the Itanna Jupyter kernel is registered.
 * This creates a kernel spec so the Itanna venv appears as
 * "Python 3 (Itanna)" in VSCode's Jupyter kernel picker.
 */
async function ensureItannaKernel(pythonBin: string, verbose: boolean): Promise<void> {
  try {
    // Check if ipykernel is available
    const checkResult = execSync(
      `"${pythonBin}" -c "import ipykernel; print('ok')" 2>/dev/null`,
      { encoding: 'utf-8', timeout: 5000 }
    ).trim();

    if (checkResult !== 'ok') {
      if (verbose) {
        console.warn('ipykernel not available in venv. Install it: pip install ipykernel');
      }
      return;
    }

    // Check if the itanna kernel is already registered
    const existingKernel = execSync(
      `"${pythonBin}" -m jupyter kernelspec list 2>/dev/null`,
      { encoding: 'utf-8', timeout: 5000 }
    );

    if (existingKernel.includes('itanna ')) {
      if (verbose) console.log('✓ Itanna Jupyter kernel already registered');
      return;
    }

    // Register the kernel
    const result = execSync(
      `"${pythonBin}" -m ipykernel install --user --name itanna --display-name "Python 3 (Itanna)" 2>&1`,
      { encoding: 'utf-8', timeout: 10000 }
    ).trim();

    console.log(`✓ Itanna Jupyter kernel registered: ${result}`);

    // Notify the user
    if (vscode.window) {
      vscode.window.showInformationMessage(
        '⚡ Itanna Jupyter kernel registered. You can now select "Python 3 (Itanna)" in your notebooks.'
      );
    }
  } catch (err) {
    if (verbose) console.warn('Failed to register Itanna Jupyter kernel:', err);
  }
}

/**
 * Derive the Itanna project root from a venv path.
 *
 * The venv can be at:
 *   - <itanna-project>/.venv/          (project-local)
 *   - ~/.itanna/.venv/                 (dedicated VSCode venv)
 *
 * In the second case, the itanna project root is still the original
 * project directory (e.g., ~/projects/itanna/).
 */
function deriveItannaRoot(venvPath: string): string | undefined {
  const parent = path.resolve(venvPath, '..');

  // Case 1: parent is the project root (project-local venv)
  if (
    fs.existsSync(path.join(parent, 'pyproject.toml')) &&
    fs.existsSync(path.join(parent, 'templates-jupyter'))
  ) {
    return parent;
  }

  // Case 2: parent is ~/.itanna (dedicated VSCode venv)
  // Look for the actual project root in common locations
  const home = process.env.HOME || '';
  const commonRoots = [
    path.join(home, 'projects', 'itanna'),
    path.join(home, 'itanna'),
    path.join(home, 'src', 'itanna'),
  ];
  for (const root of commonRoots) {
    if (
      fs.existsSync(path.join(root, 'pyproject.toml')) &&
      fs.existsSync(path.join(root, 'templates-jupyter'))
    ) {
      return root;
    }
  }

  return undefined;
}

/**
 * Activate the Itanna virtual environment.
 * Updates relevant environment variables for the extension host.
 * Returns true if successful.
 */
export async function activateVenv(verbose: boolean = false): Promise<boolean> {
  if (venvActivated) {
    return true;
  }

  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

  try {
    let venvPath: string | null = null;
    let itannaRoot: string | undefined;

    // 1. Try to find venv relative to workspace root
    if (workspaceRoot) {
      venvPath = await findVenvPath(workspaceRoot);
    }

    // 2. If not found, try known itanna directories
    if (!venvPath) {
      const home = process.env.HOME || '';
      const knownRoots = [
        path.join(home, 'projects', 'itanna'),
        path.join(home, 'itanna'),
        process.env.ITANNA_ROOT || '',
      ];
      for (const root of knownRoots) {
        if (root) {
          venvPath = await findVenvPath(root);
          if (venvPath) {
            itannaRoot = root;
            break;
          }
        }
      }
    } else {
      // Derive itanna root from venv path
      itannaRoot = deriveItannaRoot(venvPath);
    }

    if (!venvPath) {
      if (verbose) {
        vscode.window.showWarningMessage(
          'Itanna virtual environment not found. Run `poetry install` in the terminal.'
        );
      }
      return false;
    }

    // If we couldn't derive itanna root from venv, use workspace root
    if (!itannaRoot) {
      itannaRoot = workspaceRoot || undefined;
    }

    const pythonBin = path.join(venvPath, 'bin', 'python');
    if (!fs.existsSync(pythonBin)) {
      return false;
    }

    // Set environment variables for the extension host
    process.env.VIRTUAL_ENV = venvPath;
    const binDir = path.join(venvPath, 'bin');
    const currentPath = process.env.PATH || '';
    if (!currentPath.includes(binDir)) {
      process.env.PATH = `${binDir}:${currentPath}`;
    }
    const safeRoot = itannaRoot || workspaceRoot || '';
    process.env.PYTHONPATH = [
      safeRoot,
      path.join(safeRoot, 'electrical'),
      path.join(safeRoot, 'itanna'),
      process.env.PYTHONPATH || ''
    ].filter(Boolean).join(':');
    process.env.ITANNA_ROOT = safeRoot;

    // Also set for the VS Code Python extension
    const pythonConfig = vscode.workspace.getConfiguration('python');
    await pythonConfig.update(
      'defaultInterpreterPath',
      pythonBin,
      vscode.ConfigurationTarget.Workspace
    );

    // Verify activation
    const version = execSync(`"${pythonBin}" --version`, { encoding: 'utf-8' }).trim();
    console.log(`⚡ Itanna venv activated: ${venvPath} (${version})`);

    // Ensure Jupyter kernel is registered
    await ensureItannaKernel(pythonBin, verbose);

    venvActivated = true;
    return true;
  } catch (err) {
    console.error('Failed to activate Itanna venv:', err);
    return false;
  }
}

/**
 * Deactivate the virtual environment (reset env vars).
 */
export function deactivateVenv(): void {
  delete process.env.VIRTUAL_ENV;
  // Note: we can't easily undo PATH modifications, but the extension host
  // lifetime is tied to the VSCode window, so this is fine.
  venvActivated = false;
}

/**
 * Check if the Itanna venv is currently activated.
 */
export function isVenvActive(): boolean {
  return venvActivated || !!process.env.VIRTUAL_ENV;
}

/**
 * Get the Python binary path (venv or system).
 */
export function getPythonPath(): string {
  if (process.env.VIRTUAL_ENV) {
    const venvPython = path.join(process.env.VIRTUAL_ENV, 'bin', 'python');
    if (fs.existsSync(venvPython)) {
      return venvPython;
    }
  }
  return 'python3';
}

/**
 * Helper: run a command and return stdout.
 */
function execAsync(cmd: string, args: string[], options: { cwd?: string }): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = exec(
      `${cmd} ${args.join(' ')}`,
      { cwd: options.cwd, encoding: 'utf-8', timeout: 10000 },
      (err, stdout, stderr) => {
        if (err) reject(err);
        else resolve(stdout);
      }
    );
  });
}
