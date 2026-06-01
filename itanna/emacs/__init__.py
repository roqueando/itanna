"""
Emacs Integration Helpers
==========================

Functions that Emacs can call to manage Python virtual environments,
check Python availability, and provide environment info.

Usage from Emacs (Lisp):
  (let ((result (shell-command-to-string
                  \"python3 -m itanna.emacs.venv path\")))
    (message \"Venv: %s\" (string-trim result)))
"""
