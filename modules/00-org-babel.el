;;; 00-org-babel.el — Org-babel configuration for Itanna
;;; Focused on Python and Julia notebook workflows.

;; ── General org-babel settings ──────────────────────────────────────────
(setq org-confirm-babel-evaluate nil     ; Don't ask for confirmation
      org-babel-default-header-args
      '((:session . "none")
        (:results . "output replace")
        (:exports . "both")
        (:cache   . "no")
        (:noweb   . "no"))
      org-babel-python-command "python3")

;; ── Inline image display ────────────────────────────────────────────────
;; Automatically display images when opening org files and after evaluation
(setq org-display-inline-images t
      org-redisplay-inline-images t
      org-startup-with-inline-images t
      org-image-actual-width nil)  ;; Scale large images to fit the window

;; After any org-babel execution, refresh inline images
(defun itanna/org-show-inline-images-after-eval ()
  "Refresh inline image display after org-babel evaluation.

This runs after every code block execution so that plots saved
via `show_plot()` (with :results value file) appear immediately
as inline images."
  (when (and (eq major-mode 'org-mode)
             (fboundp 'org-display-inline-images))
    (org-display-inline-images)))

(add-hook 'org-babel-after-execute-hook 'itanna/org-show-inline-images-after-eval)

;; Also show images when entering org-mode (for all buffers)
(defun itanna/org-show-images-on-activate ()
  "Display inline images when org-mode is entered."
  (when (fboundp 'org-display-inline-images)
    (org-display-inline-images)))

(add-hook 'org-mode-hook 'itanna/org-show-images-on-activate)

;; ── Python default: :results value file for inline image support ────────
;; Using :results value file means:
;;   - The last expression's return value is the block result
;;   - If it's a filename (from show_plot()), it becomes [[file:...]] inline
;;   - If it's text, it's shown as-is
;;   - Persistent session (*Python-EE*) for state between blocks
(setq org-babel-default-header-args:python
      (append org-babel-default-header-args:python
              '((:session . "*Python-EE*")
                (:results . "value file")
                (:exports . "both"))))

;; ── Julia session defaults ──────────────────────────────────────────────
(setq org-babel-default-header-args:julia
      '((:session . "*Julia-EE*")
        (:results . "output")
        (:exports . "both")))

;; ── C/C++ and Rust defaults (no session, compile & run) ─────────────────
(setq org-babel-default-header-args:C
      '((:results . "output")
        (:exports . "results")))
(setq org-babel-default-header-args:C++
      '((:results . "output")
        (:exports . "results")))
(setq org-babel-default-header-args:rust
      '((:results . "output")
        (:exports . "results")))

;; ── Itanna-specific org-babel functions ─────────────────────────────────

(defun itanna/ob-python-insert-result ()
  "Evaluate the Python block at point and insert the result as a table or text.
If the result looks like a list/dict, format as an org-table."
  (interactive)
  (save-excursion
    (org-babel-previous-src-block 1)
    (let* ((info (org-babel-get-src-block-info))
           (result (org-babel-execute-src-block))
           (beg (org-babel-where-is-src-block-result nil info)))
      (if beg
          (goto-char beg)
        (org-babel-where-is-src-block-result))
      (when (and (listp result) (not (stringp result)))
        ;; Insert as org-table
        (insert
         (concat "\n"
                 (mapconcat (lambda (row)
                              (concat "| "
                                      (mapconcat (lambda (cell)
                                                   (format "%S" cell))
                                                 (if (listp row) row (list row))
                                                 " | ")
                                      " |"))
                            result
                            "\n")
                 "\n"))))))

(defun itanna/ob-julia-insert-result ()
  "Evaluate the Julia block at point and insert the result."
  (interactive)
  (save-excursion
    (org-babel-previous-src-block 1)
    (org-babel-execute-src-block)
    (org-babel-where-is-src-block-result)))

;; ── Variable inspection (Python session) ────────────────────────────────

(defun itanna/ob-python-show-vars ()
  "Show all local variables in the current Python session buffer.
Inserts the result as a code block below the current one.
Works with persistent sessions (using :session)."
  (interactive)
  (let ((session-name (org-babel-python-session-buffer
                       (org-babel-get-src-block-info))))
    (if (and session-name (get-buffer session-name))
        (progn
          (org-insert-structure-template "src")
          (insert "python :session " (buffer-name (get-buffer session-name)) "\n")
          (insert "locals()")
          (org-babel-execute-src-block))
      (message "No active Python session. Use :session header in your code block first."))))

(defun itanna/ob-julia-show-vars ()
  "Show all local variables in the current Julia session buffer."
  (interactive)
  (let ((session-name (org-babel-julia-session-buffer
                       (org-babel-get-src-block-info))))
    (if (and session-name (get-buffer session-name))
        (progn
          (org-insert-structure-template "src")
          (insert "julia :session " (buffer-name (get-buffer session-name)) "\n")
          (insert "varinfo()")
          (org-babel-execute-src-block))
      (message "No active Julia session. Use :session header in your code block first."))))

;; ── Evaluate region/block and insert below ──────────────────────────────

(defun itanna/ob-execute-and-insert-below ()
  "Execute the src block at point and insert its result as literal text below."
  (interactive)
  (org-babel-execute-src-block)
  (org-babel-where-is-src-block-result)
  (when (looking-at "[ \t]*$")
    (open-line 1)))

;; ── Org-babel keybindings (added to org-mode-map) ───────────────────────

(defvar itanna-org-babel-map
  (let ((map (make-sparse-keymap)))
    (define-key map (kbd "e")   'org-babel-execute-src-block)
    (define-key map (kbd "'")   'org-edit-special)        ; Edit in language major mode
    (define-key map (kbd "i")   'itanna/ob-execute-and-insert-below)
    (define-key map (kbd "v")   'itanna/ob-python-show-vars)
    (define-key map (kbd "V")   'itanna/ob-julia-show-vars)
    (define-key map (kbd "t")   'itanna/ob-python-insert-result)
    (define-key map (kbd "n")   'org-babel-next-src-block)
    (define-key map (kbd "p")   'org-babel-previous-src-block)
    (define-key map (kbd "d")   'org-babel-demarcate-block)
    (define-key map (kbd "s")   'org-babel-switch-to-session)
    (define-key map (kbd "k")   'org-babel-remove-result)
    map)
  "Keymap for org-babel operations in Itanna.")

;; Add to the semicolon prefix map under "o" (for org-babel)
(define-key my-semicolon-map (kbd "o") itanna-org-babel-map)

;; Also add more convenient keys in org-mode-map itself
(define-key org-mode-map (kbd "M-n") 'org-babel-next-src-block)
(define-key org-mode-map (kbd "M-p") 'org-babel-previous-src-block)

;; ── Itanna template for EE notebooks ────────────────────────────────────

(defun itanna/org-notebook-ee ()
  "Open the Itanna notebook template."
  (interactive)
  (find-file (expand-file-name "templates/org-notebook.org" itanna-root)))

(defun itanna/org-buck-calculator ()
  "Open the buck calculator template."
  (interactive)
  (find-file (expand-file-name "templates/buck-calculator.org" itanna-root)))

(defun itanna/org-executable-demo ()
  "Open the executable builder demo template."
  (interactive)
  (find-file (expand-file-name "templates/hello-executable.org" itanna-root)))

;; Add to keybindings (under ; o)
(define-key itanna-org-babel-map (kbd "N") 'itanna/org-notebook-ee)
(define-key itanna-org-babel-map (kbd "B") 'itanna/org-buck-calculator)
(define-key itanna-org-babel-map (kbd "X") 'itanna/org-executable-demo)

;;; 00-org-babel.el ends here
