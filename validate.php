<?php

# First we need to make sure we strip out any nasty stuff from the values
# that we are accepting from the browser.
$email      = mysql_real_escape_string($_GET['verification']);
$ip         = mysql_real_escape_string($_SERVER['REMOTE_ADDR']);
$name       = mysql_real_escape_string($_GET['plugin']);

# Next we need to tell the script what the database is so we can properly
# connect to it.
$dbuser     = 'USERNAME';
$dbpass     = 'PASSWORD';
$dbhost     = 'localhost';
$dbname     = 'bukget';

# try to connect to the database engine.
$dbcon      = mysql_connect($dbhost,$dbuser,$dbpass);

# Check to see if the connection was valid.  If it wasn't then die and throw
# an error.
if (!$dbcon) {
  die('Could not connect to database: ' . mysql_error());
}

# Select the database
mysql_select_db($dbname, $dbcon);

# New we need to build the query that we will be using to check to see if the
# information provided in the get is valid.
$checkquery = "SELECT id FROM repositories 
                WHERE email = '{$email}' 
                  AND ip = '{$ip}' 
                  AND plugin = '{$name}'";
               
# Get the results of the query and check to see if we were able to run the
# query without issues.  If there was an issue, then throw up an error and die   
$result     = mysql_query($checkquery, $dbcon);
if (!$result) {
  die('Could not query database...' . mysql_error());
}

# Get the number of rows returned from the query.
$numrows    = mysql_num_rows($result);

# Check to see if there were any wors returned.  1 row should return if the
# information was valid, and no rows shoudl return if it wasnt.
if ($numrows > 0) {
  # Get the row ID and then update the row to mark it validated.
  $row      = mysql_fetch_row($result);
  $repo_id  = $row[0];
  $up_query = "UPDATE repositories SET validated = 1 WHERE id = {$repo_id}";
  $update   = mysql_query($up_query, $dbcon);
  
  # if the insert didnt work, then we need to die here.
  if (!$update) {
    die('Could not query database...' . mysql_error());
  }
  
  # if we got this far then everything worked! yayz!
  header('Location: http://bukget.org/add/valid.html');
} else {
  # Looks like this was not a valid request, send the user somewhwre not nice.
  header('Location: http://bukget.org/add/invalid.html');
}
?>