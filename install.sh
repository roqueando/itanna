#!/usr/bin/env bash
#
# install.sh — Itanna Emacs Distribution Installer
#
# This script:
#   1. Symlinks ~/.emacs to the distribution's init.el
#   2. Installs the electrical Python package in development mode
#   3. Suggests missing system dependencies
#
# Usage: ./install.sh [--python-only] [--emacs-only] [--help]

set -euo pipefail

ITANNA_DIR="$(cd "$(dirname "$0")" && pwd)"
EMACS_TARGET="$HOME/.emacs"
EMACS_BACKUP="$HOME/.emacs.itanna-backup"
PYTHON_PACKAGE_DIR="$ITANNA_DIR/electrical"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

install_emacs() {
    info "Installing Emacs config..."

    if [ -L "$EMACS_TARGET" ]; then
        local current_link
        current_link="$(readlink "$EMACS_TARGET")"
        if [ "$current_link" = "$ITANNA_DIR/init.el" ]; then
            ok "~/.emacs already links to Itanna init.el"
        else
            warn "~/.emacs currently links to: $current_link"
            info "Backing up to $EMACS_BACKUP"
            cp "$EMACS_TARGET" "$EMACS_BACKUP"
            ln -sf "$ITANNA_DIR/init.el" "$EMACS_TARGET"
            ok "~/.emacs → Itanna init.el"
        fi
    elif [ -f "$EMACS_TARGET" ]; then
        warn "~/.emacs is a regular file. Backing up to $EMACS_BACKUP"
        cp "$EMACS_TARGET" "$EMACS_BACKUP"
        ln -sf "$ITANNA_DIR/init.el" "$EMACS_TARGET"
        ok "Replaced ~/.emacs with symlink to Itanna init.el"
    else
        ln -sf "$ITANNA_DIR/init.el" "$EMACS_TARGET"
        ok "Created ~/.emacs → Itanna init.el"
    fi

    # Create early-init symlink
    local early_target="$HOME/.emacs.d/early-init.el"
    if [ ! -f "$early_target" ]; then
        ln -sf "$ITANNA_DIR/early-init.el" "$early_target"
        ok "Created ~/.emacs.d/early-init.el → Itanna early-init.el"
    else
        ok "~/.emacs.d/early-init.el already exists (skipping)"
    fi

    # Create modules symlink
    local modules_target="$HOME/.emacs.d/modules"
    if [ ! -d "$modules_target" ]; then
        ln -sf "$ITANNA_DIR/modules" "$modules_target"
        ok "Created ~/.emacs.d/modules → Itanna modules/"
    else
        ok "~/.emacs.d/modules already exists (skipping)"
    fi
}

install_python() {
    info "Setting up Itanna Poetry virtual environment..."

    if ! command -v python3 &>/dev/null; then
        err "python3 not found. Install Python 3.10+ first."
        return 1
    fi

    if ! command -v poetry &>/dev/null; then
        warn "poetry not found. Installing it first..."
        pip install poetry --break-system-packages 2>&1 | tail -1
    fi

    # Ensure in-project venv
    poetry config virtualenvs.in-project true 2>/dev/null

    # Create .venv and install dependencies via poetry
    cd "$ITANNA_DIR"
    poetry lock 2>&1 | tail -3
    # Install main packages via pip inside the venv (faster than poetry for build-heavy packages)
    poetry run pip install numpy scipy matplotlib nuitka contourpy kiwisolver 2>&1 | tail -3
    # Install the itanna and electrical packages in dev mode
    poetry run pip install -e . 2>&1 | tail -1
    poetry run pip install -e ./electrical 2>&1 | tail -1

    ok "Itanna Python environment created at $ITANNA_DIR/.venv"
}

check_deps() {
    info "Checking dependencies..."

    local missing=()

    command -v emacs    >/dev/null 2>&1 || missing+=("emacs")
    command -v python3  >/dev/null 2>&1 || missing+=("python3")
    command -v julia    >/dev/null 2>&1 || missing+=("julia")
    command -v rustc    >/dev/null 2>&1 || missing+=("rustc (rust)")
    command -v gcc      >/dev/null 2>&1 || missing+=("gcc/clang")
    command -v pip3     >/dev/null 2>&1 || missing+=("pip3")

    # Recommended Python packages
    python3 -c "import numpy"      >/dev/null 2>&1 || warn "numpy not installed (pip install numpy)"
    python3 -c "import scipy"      >/dev/null 2>&1 || warn "scipy not installed (pip install scipy)"
    python3 -c "import matplotlib" >/dev/null 2>&1 || warn "matplotlib not installed (pip install matplotlib)"
    python3 -c "import nuitka"     >/dev/null 2>&1 || warn "nuitka not installed (pip install nuitka — for standalone executables)"

    if [ ${#missing[@]} -gt 0 ]; then
        warn "Missing system tools: ${missing[*]}"
    else
        ok "All core system tools found"
    fi
}

# ── Main ─────────────────────────────────────────────────────────────────

main() {
    echo ""
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║   ⚡ Itanna Distribution Installer         ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo ""

    local do_emacs=true
    local do_python=true

    for arg in "$@"; do
        case "$arg" in
            --emacs-only) do_python=false ;;
            --python-only) do_emacs=false ;;
            --help|-h)
                echo "Usage: $0 [--emacs-only] [--python-only] [--help]"
                exit 0
                ;;
        esac
    done

    # Create user data directory
    local itanna_user_dir="$HOME/.itanna/notebooks"
    if [ ! -d "$itanna_user_dir" ]; then
        mkdir -p "$itanna_user_dir"
        ok "Created $itanna_user_dir for user notebooks"
    fi

    check_deps
    echo ""

    if $do_emacs; then
        install_emacs
        echo ""
    fi

    if $do_python; then
        install_python
        echo ""
    fi

    echo "  ──────────────────────────────────────────"
    echo ""
    info "Installation complete!"
    info "Restart Emacs to load the Itanna distribution."
    echo ""
    info "Quick start:"
    echo "    Create a new EE notebook with:   ; o n  (in org-mode, or use the template)"
    echo "    Insert buck calculator:          ; E b"
    echo "    Open org-babel keybindings:      ; o"
    echo "    Find files:                      ; f"
    echo "    Magit:                           ; g"
    echo ""
    ok "Happy engineering! ⚡"
}

main "$@"
