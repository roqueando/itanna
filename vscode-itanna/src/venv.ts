// ⚡ Itanna Virtual Environment Activation
// Detects and activates the Poetry-managed Python virtual environment
// for the Itanna workspace, updating PATH and environment variables.

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { execSync, exec } from 'child_process';

let venvActivated = false;

/**
 * Find the Poetry virtual environment path for the Itanna project.
 *
 * Checks in order:
 * 1. VIRTUAL_ENV environment variable
 * 2. `.venv/` inside the workspace root
 * 3. Poetry's cache directory
 */
export async function findVenvPath(workspaceRoot: string): Promise<string | null> {
  // 1. Already activated in shell
  const envVar = process.env.VIRTUAL_ENV;
  if (envVar && fs.existsSync(envVar)) {
    return envVar;
  }

  // 2. In-project venv
  const inProjectVenv = path.join(workspaceRoot, '.venv');
  const inProjectPython = path.join(inProjectVenv, 'bin', 'python');
  if (fs.existsSync(inProjectPython)) {
    return inProjectVenv;
  }

  // 3. Poetry cache (async)
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
 * Derive the Itanna project root from a venv path.
 * The venv is typically at <itanna-root>/.venv/
 */
function deriveItannaRoot(venvPath: string): string | undefined {
  const parent = path.resolve(venvPath, '..');
  // Check if parent is the project root (has pyproject.toml + templates-jupyter)
  if (
    fs.existsSync(path.join(parent, 'pyproject.toml')) &&
    fs.existsSync(path.join(parent, 'templates-jupyter'))
  ) {
    return parent;
  }
  // Try common locations relative to the venv
  const home = process.env.HOME || '';
  const commonRoots = [
    path.join(home, 'projects', 'itanna'),
    path.join(home, 'itanna'),
  ];
  for (const root of commonRoots) {
    if (fs.existsSync(path.join(root, '.venv', 'bin', 'python'))) {
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
