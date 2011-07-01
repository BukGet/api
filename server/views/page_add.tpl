%for error in errors:
<p class="alert">{{error}}</p>
%end

%for note in notes:
<p class="info">{{note}}</p>
%end

<div class="repo_form">
  <form action="/add" method="post" cellpadding="10" cellspacing="10">
      <label for="user">Bukkit.org Name</label>
      <input type="text" name="user" id="user" class="required_text" size="32" maxlength="32"/>
      
      <label for="email">Email Address</label>
      <input type="text" id="email" name="email" class="required_email" size="46" maxlength="128"/>
      
      <label for="plugin">Plugin Name</label>
      <input type="text" id="plugin" name="plugin" class="required_text" size="32" maxlength="32"/>
      
      <label for="url">Repository URL</label>
      <input type="text" id="url" name="url" class="required_url" size="50"/>
      
      <label for="manual">Manual Activation</label>
      <input type="checkbox" id="manual" name="manual" class="buttons active" />
      
      <input type="submit" name="add" value="Submit" class="buttons cancel" />
  </form>
</div>
%rebase layout title="Add Plugin Repository"
