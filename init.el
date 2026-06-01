;;; init.el — Itanna Emacs Distribution
;;; An Emacs distribution for Electrical Engineering
;;; focusing on Python, Julia, C/C++, and Rust
;;; with org-babel notebook workflows.

;; ── Package management ──────────────────────────────────────────────────
(require 'package)
(unless (assoc "melpa" package-archives)
  (setq package-archives
        '(("melpa" . "https://melpa.org/packages/")
          ("elpa"  . "https://elpa.gnu.org/packages/"))))
(package-initialize)

;; ── Ensure core packages are installed ──────────────────────────────────
(defvar itanna-required-packages
  ;; Core UI & navigation
  '(evil evil-collection evil-escape
     ;; Completion
     vertico corfu company
     ;; Navigation & project
     projectile counsel ivy
     ;; Org & org-babel
     org org-superstar ob-rust
     ;; Languages
     julia-mode python-mode rust-mode cc-mode
     ;; Tools
     magit vterm
     ;; EE & notebooks
     )
  "Packages required by the Itanna distribution.")

(defun itanna--ensure-packages ()
  "Install any missing packages from `itanna-required-packages'."
  (let ((needs-refresh nil))
    (dolist (pkg itanna-required-packages)
      (unless (package-installed-p pkg)
        (setq needs-refresh t)))
    (when needs-refresh
      (package-refresh-contents)
      (dolist (pkg itanna-required-packages)
        (unless (package-installed-p pkg)
          (package-install pkg))))))

(itanna--ensure-packages)

;; (Modules are loaded explicitly at the bottom of init.el,
;; after all core definitions are in place.)

;; ── Core settings ───────────────────────────────────────────────────────
(setq backup-directory-alist `(("." . "~/.saves")))
(setq backup-by-copying t)
(setq delete-old-versions t
      kept-new-versions 6
      kept-old-versions 2
      version-control t)

(global-so-long-mode 1)
(electric-pair-mode 1)
(column-number-mode 1)
(display-line-numbers-mode)
(setq display-line-numbers-type 'relative)
(show-paren-mode 1)
(global-display-line-numbers-mode)

;; Font
(set-face-attribute 'default nil
                    :family "CodeNewRoman Nerd Font Mono"
                    :height 150)

;; Tab / indent preferences
(setq-default tab-width 2
              indent-tabs-mode nil
              c-basic-offset 2)

;; ── Modifier keys ───────────────────────────────────────────────────────
(setq mac-option-key-is-meta nil
      mac-command-key-is-meta t
      mac-command-modifier 'meta
      mac-option-modifier 'none)

;; ── Evil mode ───────────────────────────────────────────────────────────
;; Must set this BEFORE evil and evil-collection are loaded
(setq evil-want-keybinding nil)
(require 'evil)
(evil-mode 1)
(evil-escape-mode 1)
(setq-default evil-escape-key-sequence "jk")

;; ── Semicolon prefix map ────────────────────────────────────────────────
(define-prefix-command 'my-semicolon-map)
(define-key evil-normal-state-map (kbd ";") 'my-semicolon-map)

;; Basic ;-key bindings
(define-key my-semicolon-map (kbd "w") 'save-buffer)
(define-key my-semicolon-map (kbd "f") 'projectile-find-file)
(define-key my-semicolon-map (kbd "e") 'projectile-dired)
(define-key my-semicolon-map (kbd "C") 'projectile-compile-project)
(define-key my-semicolon-map (kbd "p") 'projectile-switch-project)
(define-key my-semicolon-map (kbd "S") 'counsel-rg)
(define-key my-semicolon-map (kbd "g") 'magit)

;; ── Vterm helper ────────────────────────────────────────────────────────
(defun open-vterm-in-project ()
  "Open a vterm buffer in the project root in a split window."
  (interactive)
  (let ((default-directory (projectile-project-root)))
    (split-window-below)
    (other-window 1)
    (vterm)))
(define-key my-semicolon-map (kbd "t") 'open-vterm-in-project)

;; ── Completion ──────────────────────────────────────────────────────────
(require 'vertico)
(vertico-mode 1)
(require 'company)
(add-hook 'after-init-hook 'global-company-mode)

;; ── Projectile ──────────────────────────────────────────────────────────
(require 'projectile)
(projectile-mode +1)
(setq projectile-indexing-method 'native)

;; ── Org mode ────────────────────────────────────────────────────────────
(setq org-adapt-indentation t
      org-hide-leading-stars t
      org-hide-emphasis-markers t
      org-pretty-entities t
      org-ellipsis "  ·"
      org-src-fontify-natively t
      org-src-tab-acts-natively t
      org-edit-src-content-indentation 0)

(add-hook 'org-mode-hook 'visual-line-mode)

;; Org priorities
(setq org-lowest-priority ?F
      org-default-priority ?E)

(setq org-priority-faces
      '((65 . "#BF616A")
        (66 . "#EBCB8B")
        (67 . "#B48EAD")
        (68 . "#81A1C1")
        (69 . "#5E81AC")
        (70 . "#4C566A")))

(setq org-todo-keywords
      '((sequence "TODO" "PROJ" "READ" "CHECK" "IDEA" "|" "DONE")))

(setq org-todo-keyword-faces
      '(("TODO"  :inherit (org-todo region) :foreground "#A3BE8C" :weight bold)
        ("PROJ"  :inherit (org-todo region) :foreground "#88C0D0" :weight bold)
        ("READ"  :inherit (org-todo region) :foreground "#8FBCBB" :weight bold)
        ("CHECK" :inherit (org-todo region) :foreground "#81A1C1" :weight bold)
        ("IDEA"  :inherit (org-todo region) :foreground "#EBCB8B" :weight bold)
        ("DONE"  :inherit (org-todo region) :foreground "#30343d" :weight bold)))

;; Org-superstar
(require 'org-superstar)
(add-hook 'org-mode-hook (lambda () (org-superstar-mode 1)))

;; Org-babel: enable languages
;; Note: ob-rust requires MELPA package; C is for C/C++ via ob-C
(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)
   (julia  . t)
   (C      . t)
   (rust   . t)
   (shell  . t)))

;; ── Language modes ──────────────────────────────────────────────────────
(require 'python-mode)
(require 'julia-mode)
(require 'rust-mode)
(require 'cc-mode)

;; ── LSP mode ────────────────────────────────────────────────────────────
(use-package lsp-mode
  :hook ((python-mode . lsp)
         (c++-mode . lsp)
         (c-mode . lsp)
         (rust-mode . lsp))
  :config
  (setq lsp-headerline-breadcrumb-enable nil)
  (setq lsp-inlay-hint-enable t)
  (setq lsp-rust-server 'rust-analyzer))

;; ── Theme ───────────────────────────────────────────────────────────────
(load-theme 'solarized-light t)

;; ── Evil collection ─────────────────────────────────────────────────────
(evil-collection-init)

;; ── Dired settings ──────────────────────────────────────────────────────
(setq dired-listing-switches "-lah")
(setq dired-dwim-target t)
(setq dired-hide-details-hide-symlink-targets nil)

;; ── Itanna-specific paths ───────────────────────────────────────────────
(defconst itanna-root
  (let ((f (or load-file-name
              (and (boundp 'byte-compile-current-file)
                   byte-compile-current-file))))
    (if f
        (file-name-directory (file-chase-links f))
      "~/.emacs.d/"))
  "Root directory of the Itanna Emacs distribution.")

(defconst itanna-electrical-path
  (expand-file-name "electrical" itanna-root)
  "Path to the electrical engineering Python package.")

;; ── Load additional modules ─────────────────────────────────────────────
(load (expand-file-name "modules/00-org-babel" user-emacs-directory) 'noerror)
(load (expand-file-name "modules/01-langs" user-emacs-directory) 'noerror)
(load (expand-file-name "modules/02-ee-tools" user-emacs-directory) 'noerror)
(load (expand-file-name "modules/03-keybindings" user-emacs-directory) 'noerror)
(load (expand-file-name "modules/04-itanna-core" user-emacs-directory) 'noerror)

;;; init.el ends here
