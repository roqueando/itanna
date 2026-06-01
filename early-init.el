;;; early-init.el — Itanna Emacs Distribution bootstrap
;;; This runs before the package system and UI are initialized.

;; Defer garbage collection
(setq gc-cons-threshold most-positive-fixnum
      gc-cons-percentage 0.6)

;; Keep the emacs.d clean
(setq user-emacs-directory (expand-file-name "~/.emacs.d/")
      package-user-dir (expand-file-name "elpa" user-emacs-directory))

;; Package archives
(setq package-archives
      '(("melpa" . "https://melpa.org/packages/")
        ("elpa"  . "https://elpa.gnu.org/packages/")))

;; Faster frame setup
(push '(menu-bar-lines . 0) default-frame-alist)
(push '(tool-bar-lines . 0) default-frame-alist)
(push '(vertical-scroll-bars) default-frame-alist)
(push '(fullscreen . maximized) default-frame-alist)

;; Native compilation settings (if available)
(when (and (fboundp 'native-comp-available-p)
           (native-comp-available-p))
  (setq native-comp-deferred-compilation t
        native-comp-async-report-warnings-errors nil))

;; Inhibit startup screen
(setq inhibit-startup-screen t
      inhibit-startup-message t
      inhibit-splash-screen t)

;; Avoid unnecessary UI elements early
(push '(scroll-bar-mode . 0) default-frame-alist)
