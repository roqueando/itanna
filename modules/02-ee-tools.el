;;; 02-ee-tools.el — Engineering tool integrations for Itanna
;;; Electrical engineering Python module, executable builder,
;;; and utility commands.

;; ── Electrical Python package path ───────────────────────────────────────
(defconst itanna-electrical-dir
  (expand-file-name "electrical" itanna-root)
  "Path to the Itanna electrical engineering Python package.")

;; Add to Python path via environment when executing org-babel blocks
(setenv "PYTHONPATH"
        (concat itanna-electrical-dir
                (if (getenv "PYTHONPATH")
                    (concat ":" (getenv "PYTHONPATH"))
                  "")))

;; ── Interactive EE calculators (org-babel wrappers) ─────────────────────

(defun itanna/ee-buck-calculator ()
  "Insert a buck converter calculation org-babel snippet."
  (interactive)
  (insert
   "#+begin_src python :results output :session *Python-EE*\n"
   "from electrical.converter.buck import design_buck\n"
   "\n"
   "# Buck converter design\n"
   "vin    = 12    # Input voltage (V)\n"
   "vout   = 3.3   # Output voltage (V)\n"
   "iout   = 2.0   # Output current (A)\n"
   "fsw    = 300e3 # Switching frequency (Hz)\n"
   "vripple = 0.01 # Output voltage ripple (V)\n"
   "\n"
   "results = design_buck(vin, vout, iout, fsw, vripple)\n"
   "for k, v in results.items():\n"
   "    print(f\"{k:20s}: {v}\")\n"
   "#+end_src\n"))

(defun itanna/ee-insert-executable ()
  "Insert an org-babel snippet to generate a standalone executable."
  (interactive)
  (insert
   "#+begin_src python :results output :session *Python-EE*\n"
   "from electrical.executable.builder import build_app\n"
   "\n"
   "def my_app():\n"
   "    \"\"\"My EE calculator app\"\"\"\n"
   "    import tkinter as tk\n"
   "    from tkinter import ttk\n"
   "\n"
   "    root = tk.Tk()\n"
   "    root.title(\"EE Calculator\")\n"
   "    ttk.Label(root, text=\"Hello from Itanna!\").pack()\n"
   "    root.mainloop()\n"
   "\n"
   "# Build standalone executable\n"
   "build_app(\n"
   "    func=my_app,\n"
   "    name=\"ee-calculator\",\n"
   "    gui=\"tkinter\",\n"
   "    output_dir=\"~/Desktop/\"\n"
   ")\n"
   "#+end_src\n"))

;; ── Run electrical module tests ─────────────────────────────────────────

(defun itanna/ee-run-tests ()
  "Run the electrical package test suite."
  (interactive)
  (let ((default-directory itanna-electrical-dir))
    (compile "python3 -m pytest tests/ -v" t)))

;; ── Open electrical package directory ───────────────────────────────────

(defun itanna/ee-open-package ()
  "Open the electrical Python package directory in dired."
  (interactive)
  (dired (expand-file-name "electrical/electrical" itanna-electrical-dir)))

;; Add keybindings
(define-key my-semicolon-map (kbd "Eb") 'itanna/ee-buck-calculator)
(define-key my-semicolon-map (kbd "Ex") 'itanna/ee-insert-executable)
(define-key my-semicolon-map (kbd "Et") 'itanna/ee-run-tests)
(define-key my-semicolon-map (kbd "Eo") 'itanna/ee-open-package)

;;; 02-ee-tools.el ends here
