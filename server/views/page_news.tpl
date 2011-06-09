%for item in news:
<div class="post">
  <h2 class="title">{{item.title}}</h2>
  <p class="meta">{{item.date}}</p>
  <div class="entry">
    {{!item.get_html()}}
  </div>
</div>
%end
%rebase layout title="News"