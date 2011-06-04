%include header title='BukGet | News'
%for item in news:
<div class="blog_post">
  <div class="blog_title">{{item.title}}</div>
  <div class="blog_date">{{item.date}}</div>
  <div class="blog_text">{{item.data}}</div>
</div>
%end
%include footer