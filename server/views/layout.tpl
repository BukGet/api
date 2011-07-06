<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <title>BukGet | {{title or 'Untitled'}}</title>
  <link rel="stylesheet" type="text/css" href="/static/css/style.css" />
  <link href="/static/plugins/hilighter/styles/shCore.css" rel="stylesheet" type="text/css" />
  <link href="/static/plugins/hilighter/styles/shThemeDefault.css" rel="stylesheet" type="text/css" />
  <script src="/static/plugins/hilighter/scripts/shCore.js" type="text/javascript"></script>
  <script src="/static/plugins/hilighter/scripts/shAutoloader.js" type="text/javascript"></script>
  %if title in ['Plugins', 'Logs']:
    <link rel="stylesheet" type="text/css" href="/static/css/no_sidebar.css" />
  %end
</head>

<body>
<div class="header">
  <div id="wrapper">
    <div id="header">
      <div id="logo">
      </div>
      <div id="navigation">
        %include navigation
      </div>
    </div>
    <div id="clear"></div>
  </div>
</div>
  <div id="wrapper" class="body">
    %if title in ['News']:
		<div id="blog">
		  %include
		</div>
    %else:
		<div id="content">
		  %include
		</div>
    %end
		<div id="sidebar">
	    %include sidebar
		</div>
		<div id="footer">
		  <div id="footer_copy">
		    BukGet Plugin Repository System
		  </div>
		  <div id="footer_nav">
		    %include navigation
			</div>
	  </div>
  </div>  
  <script type="text/javascript">
        function path() {
          var args = arguments, result = [];
          for(var i = 0;i < args.length;i++) {
            result.push(args[i].replace("@", "/static/plugins/hilighter/scripts/"))
          }
          return result
        }

        SyntaxHighlighter.autoloader.apply(null, path("bash shell\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 @shBrushBash.js", "css\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 @shBrushCss.js", "java\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 @shBrushJava.js", "js jscript javascript\u00a0 @shBrushJScript.js", "text plain\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 @shBrushPlain.js", 
        "py python\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 @shBrushPython.js"));
        
        SyntaxHighlighter.all()
  </script> 
</body>
</html>
