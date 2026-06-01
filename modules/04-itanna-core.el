;;; 04-itanna-core.el — Itanna core: venv activation, welcome page, init

;; (This module is loaded automatically by init.el)

;; ── Virtual Environment Activation ──────────────────────────────────────
;; This ensures that when Emacs opens files under ~/projects/itanna/,
;; the Python virtual environment managed by Poetry is activated.
;; This makes `org-babel` Python sessions and all `electrical.*` imports work.

(defconst itanna--venv-cache nil
  "Cached venv environment variables, lazily loaded.")

(defun itanna/ensure-venv ()
  "Ensure the Itanna Poetry virtualenv is activated in `process-environment'.

Calls `python3 -m itanna.emacs.activate env` to get the environment
variables (VIRTUAL_ENV, PATH, PYTHON, PYTHONPATH, ITANNA_ROOT) and
merges them into Emacs' `process-environment'.

This is idempotent: calling it multiple times is safe."
  (interactive)
  (let* ((venv-script (expand-file-name "itanna/emacs/activate.py" itanna-root))
         (python-path (expand-file-name "itanna" itanna-root))
         (env-lines nil))
    ;; Set PYTHONPATH so `itanna` package is importable
    (setenv "PYTHONPATH"
            (concat python-path
                    (if (getenv "PYTHONPATH")
                        (concat ":" (getenv "PYTHONPATH"))
                      "")))
    ;; Call the activation script
    (with-temp-buffer
      (call-process "python3" nil t nil "-m" "itanna.emacs.activate" "env")
      (setq env-lines
            (split-string (buffer-substring-no-properties (point-min) (point-max))
                          "\n" t)))
    ;; Apply each KEY=VALUE to process-environment
    (dolist (line env-lines)
      (when (string-match "^\\([A-Z_][A-Z_0-9]*\\)=\\(.*\\)" line)
        (let ((key (match-string 1 line))
              (val (match-string 2 line)))
          (setenv key val)
          ;; Also update exec-path for python binaries inside venv
          (when (string-equal key "PATH")
            (setq exec-path (parse-colon-path val))))))
    ;; Refresh Python path for LSP
    (when (and (fboundp 'lsp-workspace-set-configuration)
               (featurep 'lsp-mode))
      (setenv "PYTHONPATH"
              (concat itanna-electrical-dir
                      (if (getenv "PYTHONPATH")
                          (concat ":" (getenv "PYTHONPATH"))
                        ""))))
    (when (called-interactively-p 'interactive)
      (message "✅ Itanna Python environment activated"))))

;; ── Auto-activate venv on itanna file open ──────────────────────────────

(defun itanna--auto-activate-venv-hook ()
  "Hook run after a file is opened under the Itanna project."
  (when (and itanna-root
             (buffer-file-name)
             (string-prefix-p itanna-root (buffer-file-name))
             (not (minibufferp)))
    (itanna/ensure-venv)))

;; Add to find-file-hook (conditionally so it's not too aggressive)
(add-hook 'find-file-hook 'itanna--auto-activate-venv-hook)

;; ── Welcome Page ────────────────────────────────────────────────────────

(defvar itanna-welcome-buffer "*Itanna*"
  "Name of the welcome buffer.")

(defun itanna/welcome ()
  "Display the Itanna welcome page.

Calls `python3 -m itanna.cli.welcome' to generate an Org-mode string,
then displays it in a dedicated buffer in Org mode."
  (interactive)
  (itanna/ensure-venv)
  (let ((buf (get-buffer-create itanna-welcome-buffer)))
    (with-current-buffer buf
      (let ((inhibit-read-only t))
        (erase-buffer)
        (org-mode)
        (insert "#+TITLE: ⚡ Itanna — Welcome\n")
        (insert "#+DATE: " (format-time-string "%Y-%m-%d") "\n")
        (insert "#+STARTUP: overview\n")
        (insert "#+OPTIONS: ^:nil\n")
        (insert "\n")
        (insert "[[file:README.org][README]]  |  ")
        (insert "[[file:templates/org-notebook.org][New Notebook]]  |  ")
        (insert "[[file:templates/buck-calculator.org][Buck Calculator]]  |  ")
        (insert "[[file:templates/hello-executable.org][Build Executable]]  |  ")
        (insert "[[file:templates/rust-ee-template.org][Rust Template]]\n")
        (insert "\n")
        (insert "* Getting Started\n\n")
        (insert "| Keybinding | Action                          |\n")
        (insert "|------------+---------------------------------|\n")
        (insert "| ~; f~      | Find file (projectile)          |\n")
        (insert "| ~; p~      | Switch project                  |\n")
        (insert "| ~; g~      | Magit                           |\n")
        (insert "| ~; t~      | Terminal (vterm)                |\n")
        (insert "| ~; o e~    | Execute org-babel code block    |\n")
        (insert "| ~; o v~    | Inspect Python session vars     |\n")
        (insert "| ~; o N~    | New EE notebook                 |\n")
        (insert "| ~; E b~    | Insert buck calculator snippet  |\n")
        (insert "| ~; E x~    | Insert executable builder       |\n")
        (insert "| ~; R n~    | New Rust/Cargo project          |\n")
        (insert "| ~; M b~    | CMake build                     |\n")
        (insert "\n")
        (insert "* Environment\n\n")
        (insert (format "| %-18s | %-30s |\n" "Component" "Status"))
        (insert (format "|------------------+--------------------------------|\n"))
        (insert (format "| Itanna Root      | %s |\n" itanna-root))
        (insert (format "| Python           | %s |\n"
                        (shell-command-to-string "python3 --version 2>&1 | tr -d '\\n'")))
        (insert (format "| Venv Active      | %s |\n"
                        (or (getenv "VIRTUAL_ENV") "No")))
        ;; Check Python packages
        (dolist (pkg '((numpy     . "import numpy")
                       (scipy     . "import scipy")
                       (matplotlib . "import matplotlib")
                       (nuitka    . "import nuitka")))
          (let* ((pkg-name (symbol-name (car pkg)))
                 (check-cmd (cdr pkg))
                 (available (eq 0 (call-process "python3" nil nil nil
                                                 "-c" check-cmd))))
            (insert (format "| %-18s | %-30s |\n"
                            (capitalize pkg-name)
                            (if available "[X] installed" "[ ] not installed")))))
        (insert "\n")
        (insert "* Quick Reference\n\n")
        (insert "** Org-babel (prefix: ~; o~)\n\n")
        (insert "| Key   | Action                        |\n")
        (insert "|-------+-------------------------------|\n")
        (insert "| ~e~   | Execute code block            |\n")
        (insert "| ~'~   | Edit in major mode            |\n")
        (insert "| ~i~   | Execute & insert result below |\n")
        (insert "| ~v~   | Python session variables      |\n")
        (insert "| ~V~   | Julia session variables       |\n")
        (insert "| ~t~   | Insert result as org-table    |\n")
        (insert "| ~n/p~ | Next/previous block           |\n")
        (insert "| ~d~   | Demarcate block               |\n")
        (insert "| ~s~   | Switch to session buffer      |\n")
        (insert "| ~k~   | Remove result                 |\n")
        (insert "| ~N~   | New notebook                  |\n")
        (insert "| ~B~   | Buck calculator template      |\n")
        (insert "| ~X~   | Executable builder template   |\n")
        (insert "\n")
        (insert "** EE Tools (prefix: ~; E~)\n\n")
        (insert "| Key | Action                       |\n")
        (insert "|-----+------------------------------|\n")
        (insert "| ~b~ | Insert buck calculator       |\n")
        (insert "| ~x~ | Insert executable builder    |\n")
        (insert "| ~t~ | Run electrical package tests |\n")
        (insert "| ~o~ | Open electrical package dir  |\n")
        (insert "\n")
        (insert "** Rust (prefix: ~; R~)\n\n")
        (insert "| Key | Action             |\n")
        (insert "|-----+--------------------|\n")
        (insert "| ~c~ | Cargo check        |\n")
        (insert "| ~r~ | Cargo run          |\n")
        (insert "| ~t~ | Cargo test         |\n")
        (insert "| ~n~ | New Cargo project  |\n")
        (insert "\n")
        (goto-char (point-min))
        (forward-line 2)  ;; Skip #+TITLE line
        ;; Hide the front-matter
        (org-cycle)
        (set-buffer-modified-p nil)
        (read-only-mode 1)))
    (switch-to-buffer buf)
    (message "⚡ Welcome to Itanna!")))

;; ── Auto-show welcome on startup ────────────────────────────────────────

(defvar itanna-auto-welcome t
  "If non-nil, show the welcome page on Emacs startup.")

(defun itanna--maybe-show-welcome ()
  "Show the Itanna welcome page on startup if no other file is opened."
  (when itanna-auto-welcome
    ;; Wait a bit for packages to load, then show welcome
    (run-with-timer 0.5 nil
                    (lambda ()
                      (when (and (get-buffer "*scratch*")
                                 (eq (current-buffer) (get-buffer "*scratch*")))
                        (itanna/welcome))))))

;; ── Keybindings ─────────────────────────────────────────────────────────

(define-key my-semicolon-map (kbd "h") 'itanna/welcome)
(define-key my-semicolon-map (kbd "V") 'itanna/ensure-venv)

;; ── Trigger welcome on load (if this is an interactive session) ─────────
(when (and (display-graphic-p) (called-interactively-p 'interactive nil))
  (itanna--maybe-show-welcome))

;;; 04-itanna-core.el ends here
