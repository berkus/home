;; what's up?
(define-key input-decode-map "\e\eOA" [(meta up)])
(define-key input-decode-map "\e\eOB" [(meta down)])

;; key bindings
(global-set-key (kbd "M-c") 'compile)
(global-set-key (kbd "M-l") 'goto-line)
(global-set-key (kbd "C-/") 'other-window)
(global-set-key (kbd "C-c a") 'org-agenda)
(global-set-key (kbd "C-c r") 'org-capture)
(global-set-key (kbd "M-e") 'ediff-buffers)
(global-set-key (kbd "<f10>") 'server-edit)
(global-set-key (kbd "M-<up>") 'move-line-up)
(global-set-key (kbd "<f9>") 'toggle-read-only)
(global-set-key (kbd "M-<down>") 'move-line-down)
(global-set-key (kbd "C-<right>") 'next-buffer)
(global-set-key (kbd "C-<left>") 'previous-buffer)
(global-set-key (kbd "<f2>") 'delete-other-windows)
(global-set-key (kbd "M-p") 'org-publish-current-project)

;; global mode variable customizations
(setq scroll-step 1)
(setq iswitchb-mode t)
(setq icomplete-mode t)
(setq js-indent-level 2)
(setq backup-inhibited t)
(setq case-fold-search t)
(setq-default tab-width 2)
(setq p4-do-find-file nil)
(setq column-number-mode t)
(setq transient-mark-mode t)
(setq auto-save-default nil)
(setq-default fill-column 100)
(setq global-font-lock-mode t)
(setq ediff-diff-options "-w")
(setq inhibit-startup-screen t)
(setq ido-enable-flex-matching t)
(setq initial-scratch-message nil)
(setq normal-erase-is-backspace t)
(setq-default indent-tabs-mode nil)
(setq org-default-notes-file "~/.plan")
(setq frame-title-format "emacs [ %b ]")
(setq user-full-name "aldrin j d'souza")
(setq org-agenda-files (quote ("~/.plan")))
(setq-default ispell-program-name "aspell")
(setq default-input-method "devanagari-itrans")
(setq display-time-format "[%X] -- %d %B -- (%A)")
(setq battery-mode-line-format "[bat:%b%p%%:%m]---")
(add-to-list 'auto-coding-alist '("\\.org" . utf-8))
(setq uniquify-buffer-name-style (quote post-forward))
(setq ring-bell-function (lambda nil (message "*fish*")))
(setq my-elisp-dir (format "%s/%s" (file-name-directory load-file-name) ".elisp"))

;;load extra packages
(when (>= emacs-major-version 24)
  (require 'package)
   (package-initialize)
   (add-to-list 'package-archives '("marmalade" . "http://marmalade-repo.org/packages/"))
   (add-to-list 'package-archives '("melpa" . "http://melpa.milkbox.net/packages/")))

(require 'tramp)
(require 'uniquify)
(require 'yaml-mode)
(require 'cmake-mode)
(require 'jinja2-mode)
(require 'markdown-mode)
(require 'protobuf-mode)

;; file mode settings
(add-to-list 'auto-mode-alist '("\\.xml" . nxml-mode))
(add-to-list 'auto-mode-alist '("\\.xsd" . nxml-mode))
(add-to-list 'auto-mode-alist '("\\.m$" . octave-mode))
(add-to-list 'auto-mode-alist '("\\.yaml" . yaml-mode))
(add-to-list 'auto-mode-alist '("\\.md" . markdown-mode))
(add-to-list 'auto-mode-alist '("\\.txt" . markdown-mode))
(add-to-list 'auto-mode-alist '("\\.ps1" . powershell-mode))
(add-to-list 'auto-mode-alist '("\\.json" . javascript-mode))
(add-to-list 'auto-mode-alist '(".*[Cc][Mm]ake.*" . cmake-mode))
(add-to-list 'auto-mode-alist '("\\([Ss][Cc]onstruct\\|[Ss][Cc]onscript\\)" . python-mode))

;; global defaults
(fset 'yes-or-no-p 'y-or-n-p)

;; enable/disable modes.
(ido-mode t)
(menu-bar-mode 0)
(show-paren-mode t)
(display-time-mode t)
(delete-selection-mode)
(display-battery-mode t)
(if (functionp 'tool-bar-mode) (tool-bar-mode 0))
(if (functionp 'scroll-bar-mode) (scroll-bar-mode 0))

;; define functions for my hooks
(when (string= system-type "windows-nt")
  (add-hook 'window-setup-hook (lambda () (w32-send-sys-command 61488))))

(defun my-c-mode-settings()
  (c-set-style "bsd")
  (setq c-basic-offset 2)
  (setq indent-tabs-mode nil)
  (local-set-key (kbd "M-i") 'astyle-buffer)
  (add-hook 'before-save-hook 'whitespace-cleanup nil t))

(defun my-python-settings()
  (setq indent-tabs-mode nil)
  (local-set-key (kbd "M-i") 'python-tidy-buffer)
  (add-hook 'before-save-hook 'whitespace-cleanup nil t))

(defun my-js-settings()
  (setq c-basic-offset 2)
  (local-set-key (kbd "M-i") 'js-tidy-buffer))

(defun astyle-buffer()
  "invoke astyle on the buffer."
  (interactive)
  (let ((position (point)))
    (progn
      (if (executable-find "astyle")
          (shell-command-on-region
           (point-min) (point-max)
           "astyle -s2 -A1 -N -S -L -Y -w -J -o -U -k3 -p -H -z2" t t)
        (message "can't find astyle.")))
    (goto-char position)))

(defun python-tidy-buffer()
  "invoke python tidy on the buffer."
  (interactive)
  (let ((position (point)))
    (progn
      (shell-command-on-region
       (point-min) (point-max)
       (format "python %s/python-tidy.py" my-elisp-dir) t t))
    (goto-char position)))

(defun js-tidy-buffer()
  "invoke js beautifier tidy on the buffer."
  (interactive)
  (let ((position (point)))
    (progn
      (shell-command-on-region
       (point-min) (point-max)
       (format "python %s/js-beautify -i -s 2 -j" my-elisp-dir) t t))
    (goto-char position)))

;; move line up
(defun move-line-up ()
  (interactive)
  (transpose-lines 1)
  (previous-line 2))

;; move line down
(defun move-line-down ()
  (interactive)
  (next-line 1)
  (transpose-lines 1)
  (previous-line 1))

;; add hooks
(add-hook 'c-mode-common-hook 'my-c-mode-settings)
(add-hook 'python-mode-hook 'my-python-settings)
(add-hook 'js-mode-hook 'my-js-settings)

;; enabled commands.
(put 'downcase-region 'disabled nil)

;; erlang settings
(when (and (getenv "ERLANG_ROOT") (getenv "ERLANG_EMACS"))
  (progn
    (setq load-path (cons (getenv "ERLANG_EMACS") load-path))
    (setq erlang-root-dir (getenv "ERLANG_ROOT"))
    (setq exec-path (cons (concat (getenv "ERLANG_ROOT") "/bin") exec-path))
    (require 'erlang-start)))

;; org-mode settings
(setq org-capture-templates
      '(("d" "Dump" entry (file+headline "~/.plan" "Inbox")
         "* TODO %?" :kill-buffer)))
(setq org-agenda-custom-commands
      '(("d" "Daily Action List"
         ((agenda "" ((org-agenda-ndays 1)
                      (org-agenda-sorting-strategy
                       (quote ((agenda time-up priority-down tag-up))))
                      (org-deadline-warning-days 0)
                      ))))))
