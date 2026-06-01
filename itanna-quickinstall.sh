#!/usr/bin/env bash
#
# Itanna Quick Install — one-liner:  curl -fsSL https://raw.githubusercontent.com/roqueando/itanna/main/itanna-quickinstall.sh | bash
#
# What this does:
#   1. Clones the Itanna Emacs distribution from GitHub
#   2. Sets up the Poetry virtual environment with all Python deps
#   3. Symlinks ~/.emacs → itanna/init.el
#   4. Creates ~/.itanna/notebooks/ for user files
#
# Requirements: git, emacs, python3, poetry (auto-installed if missing)

set -euo pipefail

# ── Config ───────────────────────────────────────────────────────────────
REPO_URL="https://github.com/roqueando/itanna.git"
INSTALL_DIR="${ITANNA_DIR:-$HOME/projects/itanna}"
BRANCH="main"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── Header ───────────────────────────────────────────────────────────────
echo ""
echo "  ╔═══════════════════════════════════════╗"
echo "  ║   ⚡  Itanna — Quick Install           ║"
echo "  ╚═══════════════════════════════════════╝"
echo ""

# ── Check prerequisites ─────────────────────────────────────────────────
info "Checking prerequisites..."

command -v git >/dev/null 2>&1 || err "git is required. Install it first."
command -v emacs >/dev/null 2>&1 || warn "emacs not found. Install Emacs 30+ after this script."
command -v python3 >/dev/null 2>&1 || err "python3 is required."

PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
info "Python $PYTHON_VERSION found"

# Check for poetry
if ! command -v poetry >/dev/null 2>&1; then
    info "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 - 2>&1 | tail -1
    export PATH="$HOME/.local/bin:$PATH"
fi

POETRY_VERSION=$(poetry --version 2>&1)
info "$POETRY_VERSION"

# ── Clone or update the repo ────────────────────────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
    info "Updating existing installation at $INSTALL_DIR..."
    cd "$INSTALL_DIR"
    git pull origin "$BRANCH" 2>&1 | tail -1
    ok "Repository updated"
else
    info "Cloning Itanna into $INSTALL_DIR..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR" 2>&1 | tail -1
    ok "Repository cloned"
fi

cd "$INSTALL_DIR"

# ── Set up Poetry virtual environment ────────────────────────────────────
info "Setting up Python virtual environment..."
poetry config virtualenvs.in-project true 2>/dev/null

# Install main deps via pip inside the venv (faster than poetry build)
poetry env use python3 2>/dev/null || true
poetry run pip install --quiet numpy scipy matplotlib nuitka contourpy kiwisolver 2>&1 | tail -1
poetry run pip install -e . --quiet 2>&1 | tail -1
poetry run pip install -e ./electrical --quiet 2>&1 | tail -1

ok "Python environment ready at $INSTALL_DIR/.venv"

# ── Symlink Emacs config ────────────────────────────────────────────────
EMACS_TARGET="$HOME/.emacs"
EMACS_BACKUP="$HOME/.emacs.itanna-backup"

if [ -L "$EMACS_TARGET" ]; then
    CURRENT=$(readlink "$EMACS_TARGET")
    if [ "$CURRENT" = "$INSTALL_DIR/init.el" ]; then
        ok "~/.emacs already links to Itanna"
    else
        warn "~/.emacs currently links to: $CURRENT"
        info "Backing up to $EMACS_BACKUP"
        cp "$EMACS_TARGET" "$EMACS_BACKUP" 2>/dev/null || true
        ln -sf "$INSTALL_DIR/init.el" "$EMACS_TARGET"
        ok "~/.emacs → Itanna init.el"
    fi
elif [ -f "$EMACS_TARGET" ]; then
    warn "~/.emacs is a file. Backing up to $EMACS_BACKUP"
    cp "$EMACS_TARGET" "$EMACS_BACKUP"
    ln -sf "$INSTALL_DIR/init.el" "$EMACS_TARGET"
    ok "~/.emacs → Itanna init.el (backed up old config)"
else
    ln -sf "$INSTALL_DIR/init.el" "$EMACS_TARGET"
    ok "~/.emacs → Itanna init.el"
fi

# ── Symlink modules and early-init ───────────────────────────────────────
for target in modules early-init.el; do
    src="$INSTALL_DIR/$target"
    dst="$HOME/.emacs.d/$target"
    if [ ! -e "$dst" ]; then
        ln -sf "$src" "$dst"
        ok "~/.emacs.d/$target → Itanna"
    fi
done

# ── Create user data directory ───────────────────────────────────────────
USER_DIR="$HOME/.itanna/notebooks"
if [ ! -d "$USER_DIR" ]; then
    mkdir -p "$USER_DIR"
    ok "Created $USER_DIR for user notebooks"
fi

# ── Done ─────────────────────────────────────────────────────────────────
echo ""
echo "  ──────────────────────────────────────────"
echo ""
ok "Installation complete!"
info "Restart Emacs to load the Itanna distribution."
echo ""
echo "  Quick start:"
echo "    ; h        — Show welcome page"
echo "    ; o N      — Create a new notebook"
echo "    ; f        — Find files"
echo "    ; g        — Magit (Git)"
echo "    ; o e      — Execute org-babel code block"
echo ""
echo "  More info: $INSTALL_DIR/README.org"
echo ""
