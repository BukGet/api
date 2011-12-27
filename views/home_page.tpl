<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>BukGet</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link href="/static/style.css" rel="stylesheet" type="text/css" />
<script type="text/javascript" src="/static/js/cufon-yui.js"></script>
<script type="text/javascript" src="/static/js/arial.js"></script>
<script type="text/javascript" src="/static/js/cuf_run.js"></script>
</head>
<body>
<div class="main">
  <div class="header">
    <div class="header_resize">
      <div class="logo">
        <h1><a href="index.html">Buk<span>Get</span></a></h1>
      </div>
      <div class="menu_nav">
        <ul>
        </ul>
        <div class="clr"></div>
      </div>
      <div class="clr"></div>
      <div class="header_img"><img src="/static/images/main_img.png" alt="" width="271" height="234" />
        <h2>Bukkit Package Repository</h2>
        <p><strong>Making Package Installation Easy</strong><br />
        <div class="clr"></div>
      </div>
    </div>
  </div>
  <div class="clr"></div>
  <div class="content">
    <div class="content_resize">
      <div class="mainbar">
        <div class="article">
        %import markdown2
        %md = markdown2.Markdown()
        {{! md.convert(content)}}
        </div>
      </div>
      <div class="sidebar">
        <div class="gadget">
          <h2>Sidebar Menu</h2>
          <div class="clr"></div>
          <ul class="sb_menu">
            <li><a href="/">Home</a></li>
            <li><a href="/baskit">Baskit</a></li>
          </ul>
        </div>
        <div class="gadget">
          <h2><span>BukGet Enabled</span></h2>
          <div class="clr"></div>
          <ul class="ex_menu">
            <li><a href="http://spacebukkit.xereo.net/">SpaceBukkit</a><br />
              Bukkit Web Administration the awesome way</li>
          </ul>
        </div>
        <div class="gadget">
          <h2><span>Recently Updated</span></h2>
          <div class="clr"></div>
          <ul class="ex_menu">
              %for item in api['changes']:
              <li>{{item['plugin']}}</li>
              %end
          </ul>
        </div>
      </div>
      <div class="clr"></div>
    </div>
  </div>
  <div class="fbg">
    <div class="fbg_resize">
      <div class="col c1"></div>
      <div class="col c2"></div>
      <div class="col c3"></div>
      <div class="clr"></div>
    </div>
    <div class="footer">
      <p class="lf">&copy; Copyright <a href="#">BukGet</a>.</p>
      <p class="rf">Layout by Cool <a href="http://www.coolwebtemplates.net/">Website Templates</a></p>
      <div class="clr"></div>
    </div>
  </div>
</div>
</body>
</html>
