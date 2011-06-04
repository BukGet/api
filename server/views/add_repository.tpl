%include header title='BukGet | New Repository Form'
%for error in errors:
<div class="error_alert">{{error}}</div>
%end

%for note in notes:
<div class="note_alert">{{note}}</div>
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
%include footer