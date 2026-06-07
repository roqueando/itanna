# ⚡ Itanna — Electrical Engineering for VSCode

**Itanna for VSCode** brings the [Itanna Emacs Distribution](https://github.com/roqueando/itanna) experience to VSCode, replacing Org-mode/Org-babel notebooks with **Jupyter notebooks (.ipynb)** while keeping the same EE tools, templates, and workflows.

## Features

- **📓 Jupyter Notebook Templates** — Pre-built EE notebooks with buck converter calculators, executable builders, and more
- **⚡ EE Code Snippets** — Quick insert of Buck Converter, Executable Builder, and common EE patterns
- **🔌 Auto Virtual Env** — Automatically detects and activates the Poetry-managed Python venv
- **🔧 Language Tooling** — Integrated support for Python, Julia, C/C++, and Rust with proper LSP and task integration
- **🏠 Welcome Page** — Interactive landing page with environment status, keybindings, and quick actions
- **📂 Sidebar Views** — EE tools and notebook browser in the activity bar
- **🦀 Rust / 🔨 CMake Tasks** — Cargo check/run/test and CMake build tasks integrated

## Quick Start

1. Open the `itanna` workspace in VSCode
2. Install recommended extensions (prompted automatically)
3. The virtual environment activates automatically
4. Press **Ctrl+Alt+W** to see the welcome page
5. Press **Ctrl+Alt+N** to create a new EE notebook

### Keybindings

| Key | Action |
|-----|--------|
| `Ctrl+Alt+N` | New EE Notebook |
| `Ctrl+Alt+B` | Insert Buck Calculator snippet |
| `Ctrl+Alt+X` | Insert Executable Builder snippet |
| `Ctrl+Alt+T` | Run EE Tests |
| `Ctrl+Alt+W` | Show Welcome Page |
| `Ctrl+Alt+R C` | Cargo Check |
| `Ctrl+Alt+R R` | Cargo Run |
| `Ctrl+Alt+R T` | Cargo Test |
| `Ctrl+Alt+M B` | CMake Build |

Or use the Command Palette (`Ctrl+Shift+P`) and type `Itanna:`.

## Templates

Three Jupyter notebook templates are included:

| Template | Description |
|----------|-------------|
| `template-ee.ipynb` | Blank EE notebook with Python, Julia, and plotting cells |
| `buck-calculator.ipynb` | Buck converter design walkthrough |
| `hello-executable.ipynb` | Function → standalone app with Nuitka |

Create a new notebook from any template with `Itanna: New EE Notebook` or via the sidebar.

## Virtual Environment

The extension automatically detects and activates the Poetry-managed `.venv` in the workspace root. You can manually re-activate with `Itanna: Activate Virtual Environment`.

## Snippets

In any Python file or Jupyter cell, type these prefixes:

| Prefix | Snippet |
|--------|---------|
| `itanna-buck` | Buck Converter Design |
| `itanna-exec` | Executable Builder |
| `itanna-imports` | Common EE imports |
| `itanna-plot` | Matplotlib plot template |

Or use the dedicated keybindings (`Ctrl+Alt+B`, `Ctrl+Alt+X`).

## Requirements

- **VSCode** 1.85+
- **Python** 3.10+
- **Poetry** (for virtual environment management)
- **Julia** 1.9+ (optional)
- **Rust** (optional)
- **GCC/Clang** (for C/C++ compilation)

### Required VSCode Extensions

Installed automatically via workspace recommendations:

- [ms-toolsai.jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) — Jupyter notebook support
- [ms-python.python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) — Python language support
- [ms-python.vscode-pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) — Python LSP
- [julialang.language-julia](https://marketplace.visualstudio.com/items?itemName=julialang.language-julia) — Julia language support
- [rust-lang.rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer) — Rust language support
- [ms-vscode.cpptools-extension-pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools-extension-pack) — C/C++ support
- [twxs.cmake](https://marketplace.visualstudio.com/items?itemName=twxs.cmake) — CMake language support

## License

GPL-3.0-only — same as the Itanna Emacs distribution.
