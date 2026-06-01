"""
Emacs-side Virtual Environment Activation
==========================================

Generates environment variable settings that Emacs can apply
to its `process-environment` for the Itanna project.

Called from Emacs Lisp via:
    (let ((env-str (shell-command-to-string
                     "python3 -m itanna.emacs.activate env")))
      ...)

The output format is one env-var per line, KEY=VALUE, suitable
for parsing in Emacs Lisp.
"""

import os
import sys
from pathlib import Path

from .venv import _find_poetry_venv, _get_project_root


def cmd_env() -> None:
    """Print environment variables for Emacs to set, one per line."""
    venv = _find_poetry_venv()
    project_root = _get_project_root()

    if venv:
        bin_dir = venv / "bin"
        path_entries = [str(bin_dir)]
        current_path = os.environ.get("PATH", "")
        path_entries.append(current_path)
        new_path = ":".join(path_entries)

        print(f"VIRTUAL_ENV={venv}")
        print(f"PATH={new_path}")
        print(f"PYTHON={bin_dir / 'python'}")
    else:
        print(f"PATH={os.environ.get('PATH', '')}")
        print(f"PYTHON={sys.executable}")

    # Always set PYTHONPATH to include the project root for electrical package
    pythonpath = os.environ.get("PYTHONPATH", "")
    if pythonpath:
        pythonpath = f"{project_root}:{pythonpath}"
    else:
        pythonpath = str(project_root)
    print(f"PYTHONPATH={pythonpath}")
    print(f"ITANNA_ROOT={project_root}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "env"
    if cmd == "env":
        cmd_env()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
