"""
Itanna Welcome Page Generator
==============================

Generates a welcome/landing page as an Org-mode string.
Called from Emacs to display the initial buffer.

Emacs usage:
    M-: (itanna-welcome)
    or automatically on startup.
"""

import os
import sys
from datetime import date
from pathlib import Path


def get_project_info() -> dict:
    """Collect information about the Itanna installation."""
    root = Path(__file__).resolve().parent.parent.parent

    info = {
        "root": str(root),
        "version": "0.1.0",
        "date": str(date.today()),
        "python_version": sys.version.split()[0],
        "has_numpy": False,
        "has_scipy": False,
        "has_matplotlib": False,
        "has_nuitka": False,
        "venv_active": os.environ.get("VIRTUAL_ENV", ""),
    }

    # Try to detect the in-project venv
    venv_path = root / ".venv"
    if venv_path.exists() and not info["venv_active"]:
        info["venv_active"] = str(venv_path)

    try:
        import numpy
        info["has_numpy"] = True
        info["numpy_version"] = numpy.__version__
    except ImportError:
        pass

    try:
        import scipy
        info["has_scipy"] = True
        info["scipy_version"] = scipy.__version__
    except ImportError:
        pass

    try:
        import matplotlib
        info["has_matplotlib"] = True
        info["matplotlib_version"] = matplotlib.__version__
    except ImportError:
        pass

    try:
        import nuitka
        info["has_nuitka"] = True
        info["nuitka_version"] = "4.x"
    except ImportError:
        pass

    return info


def generate_welcome_org() -> str:
    """Generate the welcome page as an Org-mode string."""
    info = get_project_info()

    # Helper to make a checkbox
    def chk(val):
        return "[X]" if val else "[ ]"

    lines = [
        "#+TITLE: ⚡ Itanna — Welcome",
        "#+DATE: " + info["date"],
        "#+STARTUP: overview",
        "#+OPTIONS: ^:nil",
        "",
        "[[file:README.org][README]]  |  [[file:templates/org-notebook.org][New Notebook]]  |  [[file:templates/buck-calculator.org][Buck Calculator]]  |  [[file:templates/hello-executable.org][Build Executable]]  |  [[file:templates/rust-ee-template.org][Rust Template]]",
        "",
        "* Getting Started",
        "",
        "| Keybinding | Action                          |",
        "|------------+---------------------------------|",
        "| ~; f~      | Find file (projectile)          |",
        "| ~; p~      | Switch project                  |",
        "| ~; g~      | Magit                           |",
        "| ~; t~      | Terminal (vterm)                |",
        "| ~; o e~    | Execute org-babel code block    |",
        "| ~; o v~    | Inspect Python session vars     |",
        "| ~; o N~    | New notebook                    |",
        "| ~; E b~    | Insert buck calculator snippet  |",
        "| ~; E x~    | Insert executable builder       |",
        "| ~; R n~    | New Rust/Cargo project          |",
        "| ~; M b~    | CMake build                     |",
        "",
        "* Environment",
        "",
        f"| Component          | Status                  |",
        f"|--------------------+-------------------------|",
        f"| Itanna Root        | {info['root']} |",
        f"| Itanna Version     | {info['version']:<22s} |",
        f"| Python             | {info['python_version']:<22s} |",
        f"| Virtual Env        | {info['venv_active'] or '(none)' :<22s} |",
        f"| NumPy              | {chk(info['has_numpy'])} {info.get('numpy_version', ''):<19s} |",
        f"| SciPy              | {chk(info['has_scipy'])} {info.get('scipy_version', ''):<19s} |",
        f"| Matplotlib         | {chk(info['has_matplotlib'])} {info.get('matplotlib_version', ''):<19s} |",
        f"| Nuitka             | {chk(info['has_nuitka'])} {info.get('nuitka_version', ''):<19s} |",
        "",
        "* Recent Notebooks",
        "",
        "# This section is populated by Emacs on startup",
        "# (file:find-file \"templates/org-notebook.org\")",
        "",
        "* Quick Reference",
        "",
        "** Org-babel (prefix: ~; o~)",
        "",
        "| Key     | Action                        |",
        "|---------+-------------------------------|",
        "| ~e~     | Execute code block            |",
        "| ~'~     | Edit in major mode            |",
        "| ~i~     | Execute & insert result below |",
        "| ~v~     | Python session variables      |",
        "| ~V~     | Julia session variables       |",
        "| ~t~     | Insert result as org-table    |",
        "| ~n/p~   | Next/previous block           |",
        "| ~d~     | Demarcate block               |",
        "| ~s~     | Switch to session buffer      |",
        "| ~k~     | Remove result                 |",
        "| ~N~     | New notebook                  |",
        "| ~B~     | Buck calculator template      |",
        "| ~X~     | Executable builder template   |",
        "",
        "** EE Tools (prefix: ~; E~)",  ; Tools for electrical engineering
        "",
        "| Key     | Action                        |",
        "|---------+-------------------------------|",
        "| ~b~     | Insert buck calculator        |",
        "| ~x~     | Insert executable builder     |",
        "| ~t~     | Run electrical package tests  |",
        "| ~o~     | Open electrical package dir   |",
        "",
        "** Rust (prefix: ~; R~)",
        "",
        "| Key     | Action                        |",
        "|---------+-------------------------------|",
        "| ~c~     | Cargo check                   |",
        "| ~r~     | Cargo run                     |",
        "| ~t~     | Cargo test                    |",
        "| ~n~     | New Cargo project             |",
        "",
        "** CMake (prefix: ~; M~)",
        "",
        "| Key     | Action                        |",
        "|---------+-------------------------------|",
        "| ~b~     | CMake build                   |",
        "",
        "* Useful Commands",
        "",
        "- ~SPC s i~ or ~; o N~ — Start a new notebook",
        "- ~C-c C-c~ — Execute current org-babel code block",
        "- ~; t~ — Open a terminal in the current project",
        "- ~; g~ — Magit status",
        "- ~; f~ — Find files in the current project",
        "",
        "* Help & Configuration",
        "",
        f"- [[file:{info['root']}/README.org][Itanna README]]"
        f"- [[file:{info['root']}/init.el][Emacs Configuration (init.el)]]",
        f"- [[file:{info['root']}/electrical/electrical/converter/buck.py][Buck Converter Module]]",
        f"- [[file:{info['root']}/electrical/electrical/executable/builder.py][Executable Builder]]",
        "",
        "#+OPTIONS: toc:nil",
    ]
    return "\n".join(lines) + "\n"


def main():
    """Print the welcome page to stdout (for Emacs to capture)."""
    print(generate_welcome_org())


if __name__ == "__main__":
    main()
