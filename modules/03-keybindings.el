;;; 03-keybindings.el — Custom keybindings for the Itanna distribution

;; ── Semicolon prefix reference ──────────────────────────────────────────
;; The `;` key in normal mode is our main custom prefix.
;; Here's the full reference:

;; ; w   — save buffer
;; ; f   — projectile-find-file
;; ; e   — projectile-dired
;; ; p   — projectile-switch-project
;; ; C   — projectile-compile-project
;; ; S   — counsel-rg (search in project)
;; ; g   — magit
;; ; t   — open-vterm-in-project
;; ; k   — tabspaces: kill buffers & close workspace
;;
;; ; o   — org-babel operations:
;;   ; o e   — execute src block
;;   ; o '   — edit src block in its major mode
;;   ; o i   — execute & insert result below
;;   ; o v   — show Python session variables
;;   ; o V   — show Julia session variables
;;   ; o t   — insert Python result as org-table
;;   ; o n   — next src block
;;   ; o p   — previous src block
;;   ; o d   — demarcate (split) a src block
;;   ; o s   — switch to session buffer
;;   ; o k   — remove src block result
;;
;; ; E   — EE tools:
;;   ; E b   — insert buck converter calculator
;;   ; E x   — insert executable builder snippet
;;   ; E t   — run electrical package tests
;;   ; E o   — open electrical package dir
;;
;; ; R   — Rust tools:
;;   ; R c   — cargo check
;;   ; R r   — cargo run
;;   ; R t   — cargo test
;;   ; R n   — new cargo project
;;
;; ; M   — C/C++ / CMake:
;;   ; M b   — cmake build
;;
;; M-n   — next src block (in org-mode)
;; M-p   — previous src block (in org-mode)

;; ── Org-mode specific ───────────────────────────────────────────────────

;; Navigate source blocks quickly
(define-key org-mode-map (kbd "M-n") 'org-babel-next-src-block)
(define-key org-mode-map (kbd "M-p") 'org-babel-previous-src-block)

;; Quick insert of code block templates
(define-key org-mode-map (kbd "C-c i p") (lambda () (interactive)
                                            (org-insert-structure-template "src python")))
(define-key org-mode-map (kbd "C-c i j") (lambda () (interactive)
                                            (org-insert-structure-template "src julia")))
(define-key org-mode-map (kbd "C-c i c") (lambda () (interactive)
                                            (org-insert-structure-template "src C")))
(define-key org-mode-map (kbd "C-c i r") (lambda () (interactive)
                                            (org-insert-structure-template "src rust")))

;; ── Python mode ─────────────────────────────────────────────────────────
(define-key python-mode-map (kbd "C-c C-c") 'itanna/python-run-file)

;; ── Julia mode ──────────────────────────────────────────────────────────
(when (boundp 'julia-mode-map)
  (define-key julia-mode-map (kbd "C-c C-z") 'itanna/julia-run-repl))

;; ── C/C++ mode ──────────────────────────────────────────────────────────
(define-key c-mode-base-map (kbd "C-c C-c") 'itanna/cc-compile)

;; ── Rust mode ───────────────────────────────────────────────────────────
(define-key rust-mode-map (kbd "C-c C-c") 'itanna/rust-check)
(define-key rust-mode-map (kbd "C-c C-r") 'itanna/rust-run)
(define-key rust-mode-map (kbd "C-c C-t") 'itanna/rust-test)

;; ── Rust / Cargo keybindings (under ; R) ────────────────────────────────
(define-key my-semicolon-map (kbd "Rc") 'itanna/rust-check)
(define-key my-semicolon-map (kbd "Rr") 'itanna/rust-run)
(define-key my-semicolon-map (kbd "Rt") 'itanna/rust-test)
(define-key my-semicolon-map (kbd "Rn") 'itanna/rust-new-project)

;; ── CMake / C/C++ keybindings (under ; C) ────────────────────────────────
(define-key my-semicolon-map (kbd "Mb") 'itanna/cmake-build)

;; ── Global utils ────────────────────────────────────────────────────────

;; Restore TAB as self-insert (if needed)
;; (global-set-key (kbd "TAB") 'self-insert-command)

;; Silence bell
(setq ring-bell-function 'ignore)

;;; 03-keybindings.el ends here
