"""
Virtual Environment Detection for Emacs
=========================================

Provides the canonical path to the Itanna Poetry venv so Emacs
can activate it automatically when opening the distribution.

Emacs will call:
    python3 -m itanna.emacs.venv path
    python3 -m itanna.emacs.venv python  (returns python binary path)
    python3 -m itanna.emacs.venv info    (returns JSON blob)
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def _find_poetry_venv() -> Path | None:
    """Locate the Poetry-managed virtual environment for this project.

    Checks:
      1. VIRTUAL_ENV environment variable
      2. .venv/ inside the project root
      3. Poetry's cache directory ~/Library/Caches/pypoetry/virtualenvs/
    """
    # 1. Already activated
    venv = os.environ.get("VIRTUAL_ENV")
    if venv:
        return Path(venv)

    # 2. In-project venv
    project_root = Path(__file__).resolve().parent.parent.parent
    in_project = project_root / ".venv"
    if in_project.exists() and (in_project / "bin" / "python").exists():
        return in_project

    # 3. Poetry cache
    try:
        result = subprocess.run(
            ["poetry", "env", "info", "--path"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=10,
        )
        if result.returncode == 0:
            path = result.stdout.strip()
            if path:
                return Path(path)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def _get_project_root() -> Path:
    """Return the itanna project root directory."""
    return Path(__file__).resolve().parent.parent.parent


def cmd_path() -> None:
    """Print the venv path, or nothing if not found."""
    venv = _find_poetry_venv()
    if venv:
        print(venv)
    else:
        print("", end="")


def cmd_python() -> None:
    """Print the path to the venv's python binary."""
    venv = _find_poetry_venv()
    if venv:
        py = venv / "bin" / "python"
        if py.exists():
            print(py)
            return
    print(sys.executable)


def cmd_info() -> None:
    """Print a JSON blob with environment info."""
    venv = _find_poetry_venv()
    info = {
        "project_root": str(_get_project_root()),
        "venv_path": str(venv) if venv else None,
        "python": str(venv / "bin" / "python") if venv and (venv / "bin" / "python").exists() else sys.executable,
        "active": os.environ.get("VIRTUAL_ENV") is not None,
        "in_project_venv": (Path(_get_project_root()) / ".venv").exists(),
    }
    print(json.dumps(info, indent=2))


def cmd_activate_script() -> None:
    """Print a shell script that activates the venv.

    Emacs can source this or use it to set environment variables.
    """
    venv = _find_poetry_venv()
    if not venv:
        print("echo 'No Itanna venv found. Run: poetry install'")
        return

    bin_dir = venv / "bin"
    print(f"""# Itanna venv activation snippet (sourced by Emacs)
export VIRTUAL_ENV="{venv}"
export PATH="{bin_dir}:$PATH"
export PYTHONPATH="{_get_project_root()}:${{PYTHONPATH:-}}"
""")

    # Also print individual exports for Emacs's process-environment
    print(f"__ITANNA_VENV={venv}")
    print(f"__ITANNA_PYTHON={bin_dir / 'python'}")


if __name__ == "__main__":
    commands = {
        "path": cmd_path,
        "python": cmd_python,
        "info": cmd_info,
        "activate": cmd_activate_script,
    }
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
    handler = commands.get(cmd, cmd_info)
    handler()
