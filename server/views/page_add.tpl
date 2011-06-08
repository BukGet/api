%for error in errors:
<p class="alert">{{error}}</p>
%end

%for note in notes:
<p class="info">{{note}}</p>
%end

<div class="repo_form">
  <form action="/add" method="post">
    <table>
      <tr>
        <td>Bukkit.org Name</td>
        <td><input type="text" name="user" class="required_text" /></td>
      </tr>
      <tr>
        <td>Email Address</td>
        <td><input type="text" name="email" class="required_email" /></td>
      </tr>
      <tr>
        <td>Plugin Name</td>
        <td><input type="text" name="plugin" class="required_text" /></td>
      </tr>
      <tr>
        <td>Repository URL</td>
        <td><input type="text" name="url" class="required_url" /></td>
      </tr>
      <tr>
        <td colspan="2"><input type="submit" name="add" value="Submit" /></td>
    </table>
  </form>
</div>
%rebase layout title="Add Plugin Repository"