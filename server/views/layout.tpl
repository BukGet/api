<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <title>BukGet | {{title or 'Untitled'}}</title>
  <link rel="stylesheet" type="text/css" href="/static/css/style.css" />
  %if title in ['Plugins', 'Logs']:
    <link rel="stylesheet" type="text/css" href="/static/css/no_sidebar.css" />
  %end
</head>

<body>
  <div id="wrapper">
    <div id="header">
      <div id="logo">
      </div>
      <div id="navigation">
        %include navigation
      </div>
    </div>
		<div id="content">
		  %include
		</div>
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
</body>
</html>