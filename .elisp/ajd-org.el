(when (getenv "ORGMODE_ROOT")
  (progn
    (setq load-path (cons (concat (getenv "ORGMODE_ROOT") "/lisp") load-path))
    (setq load-path (cons (concat (getenv "ORGMODE_ROOT") "/contrib/lisp") load-path))
    (require 'org-install)))

(setq org-export-html-postamble-format '(("en" "&copy; %a [%e], %d")))

(setq org-publish-project-alist
      '(("a1drin.net-static"
         :base-directory "~/ajd/www/static"
         :base-extension "css\\|gif\\|jpg|\\js"
         :publishing-directory "~/doc/www/static"
         :recursive t
         :publishing-function org-publish-attachment)
        ("a1drin.net"
         :base-directory "~/ajd/www/pages"
         :base-extension "org"
         :email "ajdz@twitter"
         :section-numbers nil
         :table-of-contents nil
         :publishing-directory "~/doc/www"
         :style-include-default nil
         :style-include-scripts nil
         :org-publish-use-timestamps-flag nil
         :html-postamble t
         :style "
<link rel='stylesheet' href='static/style.css' type='text/css'/>
<link rel='icon' href='static/icon.ico' type='image/x-icon'/>")))

(defun add-google-analytics ()
  (goto-char (point-min))
  (search-forward "x-icon'/>")
  (insert "
<script type='text/javascript'>
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-23749928-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>
<script type='text/javascript' src='https://apis.google.com/js/plusone.js'></script>
")
  (save-buffer))

(defun add-google+1 ()
  "Adds Google +1 button"
  (let ((url (concat "http://a1drin.net/" (car (last (split-string (buffer-file-name) "/"))))))
    (progn (unless (string= url "http://a1drin.net/index.html")
             (goto-char (point-min))
             (search-forward "</h1>")
             (insert (concat 
                      "\n<div id='fb-like'>"
                      "<g:plusone size='small'></g:plusone></div>"))))))

(defun add-fb-stuff ()
  "Adds Facebook OpenGraph Plugins."
  (let ((url (concat "http://a1drin.net/" (car (last (split-string (buffer-file-name) "/"))))))
    (progn (unless (string= url "http://a1drin.net/index.html")
             (goto-char (point-min))
             (search-forward "</h1>")
             (insert (concat 
                      "\n<div id='fb-like'>"
                      "<fb:like layout='button_count' href='"
                      url
                      "'</fb:like></div>\n"))
             (goto-char (point-min))
             (search-forward "x-icon'/>")
             (insert "<script src='http://connect.facebook.net/en_US/all.js#xfbml=1'></script>")
             (goto-char (point-max))
             (search-backward "</div>")
             (insert (concat
                 "<div id='fb-comments'>"
                 "<fb:comments num_posts='2' href='"
                 url
                 "'</fb:comments></div>\n"))
             (goto-char (point-min))
             (search-forward "souza\"/>")
             (insert (concat
                      "\n<meta property='og:type' content='article'/>"
                      "\n<meta property='og:url' content='"
                      url
                      "'/>"
                      "\n<meta property='og:site_name' content=\"aldrin's pages\"/>"
                      "\n<meta property='fb:app_id' content='171555669572704'/>"
                      "\n<meta property='fb:admins' content='536652068'/>"))
             (save-buffer)))))

(add-hook 'org-publish-after-export-hook 'add-google-analytics)
(add-hook 'org-publish-after-export-hook 'add-google+1)
(provide 'ajd-org)
