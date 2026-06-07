#!/usr/bin/env bash
#
# install-vscode-adapter.sh — Install the Itanna VSCode adapter
#
# This script:
#   1. Installs the VSCode extension dependencies (npm)
#   2. Compiles the TypeScript extension
#   3. Symlinks or installs the extension for development
#
# Usage: ./scripts/install-vscode-adapter.sh [--link-only] [--help]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ITANNA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
EXTENSION_DIR="$ITANNA_DIR/vscode-itanna"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

check_deps() {
    info "Checking dependencies..."
    
    if ! command -v node &>/dev/null; then
        err "Node.js not found! Install from https://nodejs.org/"
        exit 1
    fi
    
    if ! command -v npm &>/dev/null; then
        err "npm not found! It should come with Node.js."
        exit 1
    fi
    
    if ! command -v code &>/dev/null; then
        warn "VSCode CLI (code) not found in PATH."
        warn "The extension will be compiled but not auto-installed."
        warn "Install it manually from the VSIX file."
        HAS_CODE=false
    else
        HAS_CODE=true
    fi
    
    local node_ver=$(node --version)
    local npm_ver=$(npm --version)
    ok "Node.js $node_ver, npm $npm_ver"
}

install_vscode_deps() {
    if [ "$HAS_CODE" = false ]; then
        warn "code CLI not found. Skipping VSCode extension installation."
        return
    fi
    
    info "Installing required VSCode extensions..."
    
    # Jupyter extension (core requirement for notebooks)
    code --install-extension ms-toolsai.jupyter --force 2>&1 || true
    code --install-extension ms-toolsai.jupyter-keymap --force 2>&1 || true
    code --install-extension ms-toolsai.jupyter-renderers --force 2>&1 || true
    
    # Python
    code --install-extension ms-python.python --force 2>&1 || true
    code --install-extension ms-python.vscode-pylance --force 2>&1 || true
    
    ok "Required VSCode extensions installed"
}

install_deps() {
    info "Installing npm dependencies..."
    cd "$EXTENSION_DIR"
    
    if [ ! -f "package.json" ]; then
        err "package.json not found in $EXTENSION_DIR"
        exit 1
    fi
    
    npm install
    ok "npm dependencies installed"
}

compile_extension() {
    info "Compiling TypeScript extension..."
    cd "$EXTENSION_DIR"
    
    if [ ! -f "node_modules/.package-lock.json" ]; then
        warn "node_modules not found. Running npm install first..."
        npm install
    fi
    
    npx tsc -p ./tsconfig.json
    ok "Extension compiled to $EXTENSION_DIR/out/"
}

install_jupyter_kernel() {
    info "Setting up Jupyter kernel for Itanna venv..."
    
    local venv_python="$ITANNA_DIR/.venv/bin/python"
    if [ ! -f "$venv_python" ]; then
        warn "Itanna venv not found at $ITANNA_DIR/.venv"
        warn "Run 'poetry install' first, then run this script again."
        return 1
    fi
    
    # Ensure ipykernel is installed
    "$venv_python" -c "import ipykernel" 2>/dev/null || {
        info "Installing ipykernel..."
        "$venv_python" -m pip install ipykernel 2>&1 | tail -2
    }
    
    # Register the Itanna kernel
    local kernel_check
    kernel_check=$("$venv_python" -m jupyter kernelspec list 2>/dev/null | grep "itanna " || echo "")
    if [ -z "$kernel_check" ]; then
        info "Registering Itanna Jupyter kernel..."
        "$venv_python" -m ipykernel install --user --name itanna --display-name "Python 3 (Itanna)" 2>&1
        ok "Jupyter kernel 'Python 3 (Itanna)' registered"
    else
        ok "Jupyter kernel already registered"
    fi
}

install_extension() {
    info "Installing extension in VSCode..."

    cd "$EXTENSION_DIR"

    # Try to use vsce to package and install
    local VSIX_FILE=""

    if npm list @vscode/vsce &>/dev/null || npm list -g @vscode/vsce &>/dev/null; then
        info "Packaging extension as VSIX using @vscode/vsce..."
        npx @vscode/vsce package --out itanna-vscode.vsix 2>&1 || true
        if [ -f "itanna-vscode.vsix" ]; then
            VSIX_FILE="itanna-vscode.vsix"
            ok "VSIX packaged: itanna-vscode.vsix"
        fi
    fi

    if [ -n "$VSIX_FILE" ] && [ "$HAS_CODE" = true ]; then
        info "Installing VSIX via code CLI..."
        # Remove any previous version first (both naming patterns)
        rm -rf "$HOME/.vscode/extensions/itanna-vscode"* 2>/dev/null || true
        rm -rf "$HOME/.vscode/extensions/itanna-ee.itanna-vscode"* 2>/dev/null || true
        local install_out
        install_out=$(code --install-extension "$VSIX_FILE" --force 2>&1) || true
        echo "$install_out"
        if echo "$install_out" | grep -qi "successfully installed"; then
            ok "Extension installed from VSIX"
        elif echo "$install_out" | grep -qi "restart"; then
            warn "VSCode needs to be restarted to load the extension."
            warn "Close and reopen VSCode, or run: code --reload-window"
        fi
        return
    fi

    # Fallback: copy extension files directly to VSCode extensions directory
    if [ "$HAS_CODE" = true ]; then
        local ext_dir="$HOME/.vscode/extensions/itanna-vscode-0.1.0"
        info "Installing extension directly to $ext_dir ..."
        
        mkdir -p "$ext_dir"
        
        # Copy all essential extension files
        cp -f "$EXTENSION_DIR/package.json" "$ext_dir/"
        cp -f "$EXTENSION_DIR/README.md" "$ext_dir/" 2>/dev/null || true
        cp -f "$EXTENSION_DIR/tsconfig.json" "$ext_dir/" 2>/dev/null || true
        
        # Copy compiled output
        if [ -d "$EXTENSION_DIR/out" ]; then
            rm -rf "$ext_dir/out"
            cp -r "$EXTENSION_DIR/out" "$ext_dir/out"
        fi
        
        # Copy snippets
        if [ -d "$EXTENSION_DIR/snippets" ]; then
            mkdir -p "$ext_dir/snippets"
            cp -r "$EXTENSION_DIR/snippets/"* "$ext_dir/snippets/" 2>/dev/null || true
        fi
        
        # Copy resources
        if [ -d "$EXTENSION_DIR/resources" ]; then
            mkdir -p "$ext_dir/resources"
            cp -r "$EXTENSION_DIR/resources/"* "$ext_dir/resources/" 2>/dev/null || true
        fi
        
        # Copy node_modules (needed at runtime)
        if [ -d "$EXTENSION_DIR/node_modules" ]; then
            rm -rf "$ext_dir/node_modules"
            cp -r "$EXTENSION_DIR/node_modules" "$ext_dir/node_modules"
        fi
        
        ok "Extension copied to $ext_dir"
        
        # Reload VSCode window to pick up the extension
        info "Reloading VSCode window..."
        code --reload-window 2>/dev/null || true
        
        warn "If the extension doesn't appear, run: code --install-extension $(ls $EXTENSION_DIR/*.vsix 2>/dev/null | head -1) --force"
        warn "Or press F5 in $EXTENSION_DIR for Extension Development Host mode."
    else
        warn "'code' CLI not found. To install manually:"
        warn "  1. Copy the extension directory:"
        warn "     cp -r $EXTENSION_DIR/out $HOME/.vscode/extensions/itanna-vscode-0.1.0/"
        warn "  2. Reload VSCode"
    fi
}

show_instructions() {
    echo ""
    echo "  ──────────────────────────────────────────"
    echo ""
    info "Installation complete!"
    echo ""
    echo "  To use the extension:"
    echo "    1. Open the itanna workspace in VSCode:"
    echo "       code $ITANNA_DIR"
    echo ""
    echo "    2. Install recommended extensions (prompted automatically)"
    echo ""
    echo "    3. Press Ctrl+Alt+W for the welcome page"
    echo "       or Ctrl+Alt+N for a new EE notebook"
    echo ""
    echo "  For development (F5 launch):"
    echo "    1. Open $EXTENSION_DIR in VSCode"
    echo "    2. Press F5 to launch Extension Development Host"
    echo "    3. The Itanna extension will be active"
    echo ""
}

# ── Main ─────────────────────────────────────────────────────────────────

main() {
    echo ""
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║   ⚡ Itanna — VSCode Adapter Installer    ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo ""
    
    local do_link=false
    for arg in "$@"; do
        case "$arg" in
            --link-only) do_link=true ;;
            --help|-h)
                echo "Usage: $0 [--link-only] [--help]"
                exit 0
                ;;
        esac
    done
    
    check_deps
    echo ""
    
    if [ "$do_link" = false ]; then
        install_deps
        compile_extension
    fi
    
    install_vscode_deps
    echo ""
    install_extension
    echo ""
    install_jupyter_kernel
    echo ""
    show_instructions
}

main "$@"
