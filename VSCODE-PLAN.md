# ⚡ Itanna for VSCode + Jupyter — Plan

## Goal

Port the **Itanna Emacs Distribution for Electrical Engineering** to VSCode, replacing Org-mode/Org-babel notebooks with **Jupyter notebooks (.ipynb)** while keeping the same EE tools, templates, and workflows.

## Architecture

```
~/projects/itanna/
├── .vscode/
│   ├── extensions.json          # Recommended extensions
│   ├── settings.json            # Workspace settings
│   └── tasks.json               # Build/test tasks
├── vscode-itanna/               # VSCode extension directory
│   ├── package.json
│   ├── README.md
│   ├── src/
│   │   ├── extension.ts         # Extension entry point
│   │   ├── commands.ts          # Command registrations
│   │   ├── templates.ts         # Jupyter notebook templates
│   │   ├── snippets.ts          # EE code snippets
│   │   ├── venv.ts              # Virtual env activation
│   │   ├── welcome.ts           # Welcome page (webview)
│   │   ├── status.ts            # Status bar items
│   │   ├── treeView.ts          # Custom tree views
│   │   └── testRunner.ts        # Electrical package test runner
│   ├── resources/
│   │   └── welcome/             # Welcome page assets
│   └── syntaxes/                # (optional) custom grammars
├── templates-jupyter/           # Jupyter notebook templates
│   ├── template-ee.ipynb        # Blank EE notebook
│   ├── buck-calculator.ipynb    # Buck converter design
│   └── hello-executable.ipynb   # Executable builder demo
├── .venv/                       # Poetry-managed virtual env (shared)
├── electrical/                  # Python EE package (unchanged)
└── itanna/                      # Python support package (unchanged)
```

## Phases

### Phase 1: Foundation — Project Structure & Workspace Config
- [ ] Create `.vscode/settings.json` with workspace settings
- [ ] Create `.vscode/extensions.json` recommending Jupyter, Python, Julia, Rust extensions
- [ ] Create `.vscode/tasks.json` for EE tasks
- [ ] Set up the VSCode extension scaffold (`vscode-itanna/`)

### Phase 2: Core Extension — Commands, Venv, Status Bar
- [ ] Implement `extension.ts` with activation/deactivation
- [ ] Register all Itanna commands in `commands.ts`
- [ ] Implement virtual environment detection & activation in `venv.ts`
- [ ] Add status bar items showing venv status, EE tools
- [ ] Implement welcome page as a webview

### Phase 3: Jupyter Notebook Integration
- [ ] Create Jupyter notebook templates (`.ipynb` files)
- [ ] Implement command to create new EE notebook from template
- [ ] Create EE cell snippets (buck converter, executable builder)
- [ ] Add custom code lenses or toolbar actions for EE workflows

### Phase 4: Electrical Engineering Tools
- [ ] Snippet: Insert buck converter calculator
- [ ] Snippet: Insert executable builder
- [ ] Command: Run electrical package tests
- [ ] Command: Open electrical package directory
- [ ] Command: Open buck calculator template
- [ ] Command: Open executable builder template

### Phase 5: Language-Specific Tooling
- [ ] Python: EE-specific settings (venv activation, test config)
- [ ] Julia: Julia for Jupyter notebook support
- [ ] C/C++: CMake integration via tasks
- [ ] Rust: Cargo task integration (check, run, test, new project)

### Phase 6: Polish & Documentation
- [ ] Extension README
- [ ] Keybinding reference
- [ ] Debug configuration
- [ ] Installation script

## Emacs → VSCode Mapping

| Emacs Feature                  | VSCode Equivalent                               |
|--------------------------------|--------------------------------------------------|
| Org-mode notebooks            | Jupyter notebooks (.ipynb)                       |
| Org-babel code blocks         | Jupyter code cells                               |
| `; o e` Execute code block    | `Shift+Enter` or cell run button                 |
| `; o N` New notebook          | Command: "Itanna: New EE Notebook"                |
| `; E b` Insert buck calc      | Snippet: prefix `itanna-buck` or command         |
| `; E x` Insert exec builder   | Snippet: prefix `itanna-exec` or command         |
| `; E t` Run tests             | Command: "Itanna: Run EE Tests"                  |
| `; E o` Open EE package       | Command: "Itanna: Open EE Package"               |
| `; h` Welcome page            | Command: "Itanna: Show Welcome" + webview        |
| `; V` Activate venv           | Auto-activated + status bar indicator            |
| `; R c` Cargo check           | Task: Cargo Check                                |
| `; R r` Cargo run             | Task: Cargo Run                                  |
| `; R t` Cargo test            | Task: Cargo Test                                 |
| `; M b` CMake build           | Task: CMake Build                                |
| Org-babel inline images       | Jupyter inline matplotlib output                 |
| Org-table result              | Pandas DataFrame display in Jupyter              |

## Keybindings (VSCode)

All Itanna commands use the prefix `Itanna:` and can be bound:

| Command                              | Recommended Keybinding        |
|--------------------------------------|-------------------------------|
| Itanna: New EE Notebook              | `Ctrl+Alt+N`                  |
| Itanna: Insert Buck Calculator       | `Ctrl+Alt+B`                  |
| Itanna: Insert Executable Builder    | `Ctrl+Alt+X`                  |
| Itanna: Show Welcome                 | `Ctrl+Alt+W`                  |
| Itanna: Run EE Tests                 | `Ctrl+Alt+T`                  |
| Itanna: Open EE Package              | `Ctrl+Alt+O`                  |
| Itanna: Activate Virtual Environment | (auto on workspace open)      |
| Itanna: Cargo Check                  | `Ctrl+Alt+R C`                |
| Itanna: Cargo Run                    | `Ctrl+Alt+R R`                |
| Itanna: Cargo Test                   | `Ctrl+Alt+R T`                |
| Itanna: Cargo New Project            | `Ctrl+Alt+R N`                |
| Itanna: CMake Build                  | `Ctrl+Alt+M B`                |

## Python Package Reuse

The `electrical/` and `itanna/` Python packages are **shared** between Emacs and VSCode — no changes needed.
The `.venv` managed by Poetry is also shared.

## Templates

Jupyter notebook templates live in `templates-jupyter/`. They mirror the .org templates:

- `templates-jupyter/template-ee.ipynb` → `templates/org-notebook.org`
- `templates-jupyter/buck-calculator.ipynb` → `templates/buck-calculator.org`
- `templates-jupyter/hello-executable.ipynb` → `templates/hello-executable.org`

## Required VSCode Extensions

| Extension                          | Purpose                    |
|------------------------------------|----------------------------|
| `ms-toolsai.jupyter`              | Jupyter notebook support   |
| `ms-python.python`                | Python language support    |
| `ms-python.vscode-pylance`        | Python LSP                 |
| `julialang.language-julia`        | Julia language support     |
| `rust-lang.rust-analyzer`         | Rust language support      |
| `ms-vscode.cpptools-extension-pack` | C/C++ support            |
| `twxs.cmake`                      | CMake language support     |
| `vadimcn.vscode-lldb`             | Rust/C++ debugger          |
