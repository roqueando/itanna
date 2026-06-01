;;; 01-langs.el — Language-specific configuration for Itanna
;;; Python, Julia, C/C++, Rust

;; ── PYTHON ───────────────────────────────────────────────────────────────
(require 'python-mode)

;; Python compile/run helper for org-babel executor
(defun itanna/python-run-file ()
  "Run the current Python file in a compilation buffer."
  (interactive)
  (compile (format "python3 %s" (buffer-file-name)) t))

;; Add to org-mode so org-babel can find the right Python
(setq org-babel-python-command "python3")

;; ── JULIA ────────────────────────────────────────────────────────────────
(require 'julia-mode)

;; Julia inferior mode (REPL integration)
(defun itanna/julia-run-repl ()
  "Start an inferior Julia REPL."
  (interactive)
  (when (fboundp 'inferior-julia)
    (inferior-julia))
  (when (fboundp 'run-julia)
    (run-julia)))

;; ── C/C++ ────────────────────────────────────────────────────────────────
(require 'cc-mode)

;; C/C++ compile helper
(defun itanna/cc-compile ()
  "Compile the current buffer using a sensible default."
  (interactive)
  (let ((file (buffer-file-name)))
    (cond
     ((string-match "\\.c$" file)
      (compile (format "gcc -Wall -Wextra -o %s %s"
                       (file-name-sans-extension (file-name-nondirectory file))
                       file) t))
     ((string-match "\\.cpp$" file)
      (compile (format "g++ -Wall -Wextra -o %s %s"
                       (file-name-sans-extension (file-name-nondirectory file))
                       file) t))
     ((string-match "\\.h$" file)
      (message "Header file — nothing to compile"))
     (t (call-interactively 'compile)))))

;; ── RUST ─────────────────────────────────────────────────────────────────
(require 'rust-mode)

;; Rust compile/check
(defun itanna/rust-check ()
  "Run cargo check in the project directory."
  (interactive)
  (let ((default-directory (or (projectile-project-root)
                               default-directory)))
    (compile "cargo check" t)))

(defun itanna/rust-run ()
  "Run cargo run in the project directory."
  (interactive)
  (let ((default-directory (or (projectile-project-root)
                               default-directory)))
    (compile "cargo run" t)))

(defun itanna/rust-test ()
  "Run cargo test in the project directory."
  (interactive)
  (let ((default-directory (or (projectile-project-root)
                               default-directory)))
    (compile "cargo test" t)))

(defun itanna/rust-new-project (name)
  "Create a new Rust Cargo project and open it."
  (interactive "sProject name: ")
  (let ((default-directory (or (projectile-project-root) default-directory)))
    (compile (format "cargo new --bin %s" name) t)))

;; ── C/C++ ────────────────────────────────────────────────────────────────

(defun itanna/cmake-build ()
  "Create a build directory and run cmake."
  (interactive)
  (let ((build-dir (expand-file-name "build" (or (projectile-project-root)
                                                   default-directory))))
    (unless (file-directory-p build-dir)
      (make-directory build-dir))
    (let ((default-directory build-dir))
      (compile "cmake .. && make -j$(sysctl -n hw.ncpu)" t))))

;;; 01-langs.el ends here
