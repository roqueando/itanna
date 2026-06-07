# ⚡ Ayedero Emacs Distribution Plan

## Context

An Emacs distribution focused on Electrical Engineering, built on top of the existing `~/ayedero/.emacs` config. The goal is to create a cohesive, modular distribution that:

1. **Targets 4 languages**: Python, Julia, C/C++, Rust
2. **Org-mode + Org-babel** as the central notebook interface (Python & Julia only for notebooks)
3. **A Python electrical engineering module** (`electrical`) that grows over time (e.g., `electrical.converter.buck`)
4. **Standalone executable generation** from Python functions (Nuitka + Tkinter/PySide6), callable from org-babel blocks
5. **Custom keybindings** for Org-babel interaction and EE-specific workflows

## What already exists

- **`~/.emacs`** → symlink to `~/ayedero/.emacs` — a full Emacs config with:
  - Evil mode, Evil-collection
  - Package management (MELPA + ELPA)
  - Tabspaces/workspaces
  - LSP mode (Python, C/C++, Rust, Go, Haskell, etc.)
  - Julia mode, Python mode, CC mode, Rust mode already installed
  - Org mode, Org-superstar
  - Projectile, Magit, Corfu, Company, Vertico
  - A `my-semicolon-map` prefix `;` for custom keybindings
- **`~/eletronics/`** — existing EE projects (circuit-simulator, lumina/rgb.py, aula8.py)
- **Languages installed**: Python 3.14.3, Julia 1.12.6, Rust 1.95.0, Apple Clang 17
- **ELPA packages**: julia-mode, python-mode, rust-mode, cc-mode already present

## What needs to be added/created

### 1. Emacs Distribution Structure
- Base directory: `~/projects/itanna/`
- Split init into modular `.el` files inside `~/projects/itanna/`
- Add an `early-init.el` for distribution bootstrap
- Provide an install script that symlinks `~/.emacs` to the distribution init

### 2. Org-babel Enhancements
- Ensure `ob-python` and `ob-julia` are configured
- Add `ob-julia` if not bundled (check Emacs 30.1 availability)
- **Custom keybindings for Org-babel**:
  - Execute block (`C-c C-c` equivalent) — already exists
  - Session management keys for Python/Julia
  - Variable inspector/interaction keys
- **Jupyter kernel integration** (optional — `emacs-jupyter` or `ein` packages)

### 3. Python EE Module (`electrical`)
- Python package at `~/projects/itanna/electrical/`
- Structured as a pip-installable package (pyproject.toml)
- Start with converter modules:
  - `electrical.converter.buck` — Buck converter component calculator
- Future modules: boost, flyback, filters, op-amp, transmission lines, etc.

### 4. Standalone Executable Generator
- A Python module `electrical.executable` (or separate `ee-tools`)
- Takes a Python function + metadata and builds a standalone app with Nuitka
- Tkinter and/or PySide6 GUI generation
- Can be invoked from org-babel code blocks

### 5. C/C++ and Rust Integration
- LSP already configured
- CMake integration, Cargo project templates

### 6. General Configuration
- Fix tree-sitter library issue (0.25 vs 0.26 version mismatch)
- Tkinter installation (missing `_tkinter`)
- Nuitka installation
- Possibly a dedicated Jupyter/notebook Emacs setup

## Files/Directories to Create

```
~/projects/itanna/
├── init.el                     # Entry point (symlinked from ~/.emacs)
├── early-init.el               # Package bootstrap, performance
├── README.org                  # Documentation
├── install.sh                  # Setup script
├── modules/
│   ├── 00-org-babel.el         # Org-babel configuration + keybindings
│   ├── 01-langs.el             # Language-specific configs
│   ├── 02-ee-tools.el          # EE tool integrations
│   └── 03-keybindings.el       # Custom keybindings
├── electrical/                 # Python EE package
│   ├── pyproject.toml
│   ├── electrical/
│   │   ├── __init__.py
│   │   ├── converter/
│   │   │   ├── __init__.py
│   │   │   ├── buck.py
│   │   │   ├── boost.py        # (future)
│   │   │   └── flyback.py      # (future)
│   │   ├── filters/            # (future)
│   │   ├── transmission/       # (future)
│   │   └── executable/
│   │       ├── __init__.py
│   │       └── builder.py      # Nuitka/Tkinter/PySide builder
│   └── tests/
└── templates/
    ├── org-notebook.org        # EE notebook template
    ├── buck-calculator.org     # Example notebook
    └── hello-executable.org    # Example: function → standalone
```

## Questions for the User

1. **Split vs monolithic init**: Keep the existing single `init.el` with well-organized sections, or split into multiple module files in `~/projects/itanna/modules/`?

2. **Org-babel for Julia**: Do you want `ob-julia` from MELPA (community package) or is built-in Emacs 30 `ob-julia` sufficient?

3. **Jupyter integration**: Do you want actual Jupyter kernel integration (via `emacs-jupyter` or `ein`) for nicer notebook experience, or pure org-babel (code blocks executed inline) is enough?

4. **Variable interaction UI**: For "interacting with Python/Julia variables" — do you envision:
   - A sidebar showing session variables?
   - Org-mode tables that sync with Python/Julia variables?
   - A REPL buffer integration?
   - Something simpler like keybindings that evaluate and insert variable values?

5. **GUI preference for executables**: Tkinter vs PySide6 as primary? PySide6 is richer but heavier. Tkinter is simpler and already the default for Nuitka.

6. **Naming**: Is "Ayedero EE" / "Itanna" a good name, or do you have another name in mind?

7. **Should the `electrical` Python package be a separate Git repo** (pip-installable) or bundled inside the Emacs distribution?

## VSCode + Jupyter Adapter

**Status: In progress** — see `VSCODE-PLAN.md` for full plan

An adapter that ports the Itanna experience to VSCode + Jupyter notebooks.

### Files Created

```
.vscode/
├── extensions.json        # Recommended VSCode extensions
├── settings.json          # Workspace settings
└── tasks.json             # Build/test/run tasks

vscode-itanna/             # VSCode extension
├── package.json           # Extension manifest
├── tsconfig.json          # TypeScript config
├── README.md              # Extension documentation
├── src/
│   ├── extension.ts       # Extension entry point
│   ├── commands.ts        # All command registrations
│   ├── venv.ts            # Virtual env detection & activation
│   ├── templates.ts       # Notebook template management
│   ├── snippets.ts        # Programmatic snippet insertion
│   ├── welcome.ts         # Welcome page webview
│   ├── treeView.ts        # Sidebar tree views
│   ├── status.ts          # Status bar indicators
│   └── testRunner.ts      # EE test runner
├── snippets/
│   └── python.json        # Python code snippets
└── resources/
    ├── icon-sidebar.svg
    ├── icon-tools.svg
    └── icon-notebook.svg

templates-jupyter/         # Jupyter notebook templates
├── template-ee.ipynb      # Blank EE notebook
├── buck-calculator.ipynb  # Buck converter design
└── hello-executable.ipynb # Executable builder demo

scripts/
└── install-vscode-adapter.sh  # Install script
```

### Key Mappings

| Emacs Org-babel               | VSCode + Jupyter                |
|-------------------------------|----------------------------------|
| `; o e` Execute block         | `Shift+Enter`                    |
| `; o N` New notebook          | `Ctrl+Alt+N`                     |
| `; E b` Insert buck calc      | `Ctrl+Alt+B` or snippet          |
| `; E x` Insert exec builder   | `Ctrl+Alt+X` or snippet          |
| `; E t` Run tests             | `Ctrl+Alt+T`                     |
| `; h` Welcome page            | `Ctrl+Alt+W` (webview)           |
| `; V` Activate venv           | Auto-activate + status bar       |
| `; R c` / `; R r` / `; R t`  | Tasks: Cargo Check/Run/Test      |
| `; M b` CMake build           | Task: CMake Build                |

### To Install & Use

```bash
# Install npm deps and compile
./scripts/install-vscode-adapter.sh

# Or just compile (after manual npm install)
cd vscode-itanna && npm install && npm run compile

# Open workspace in VSCode
code .
```

Then press `Ctrl+Alt+W` for the welcome page or `Ctrl+Alt+N` for a new notebook.
