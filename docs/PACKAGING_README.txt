BukGet Packaging Howto
----------------------

1) All BukGet Packages are Zip files.

2) BukGet Packages are required to have etc, bin, and lib folders in the
   package root.  These folder can be empty, however are needed in order to
   pass the check.

3) There must be at least 1 jar file within the package.  If there is no java
   binary then what are you generating a package for? :-p

4) It is preferable to package in any libraries you may need into the package.
   if you would prefer to alternatively package the libraries separately, make
   sure that the library doesn't already exist in the repository.


LAYOUT:
-------

/plugins/
/libs/


FIELD INFORMATION FOR repo.json:
--------------------------------

name          This is reserved for the plugin name.  The name cannot have any
              spaces.  This is used to generate the folder names and to
              properly name the jar file when it is placed in the plugins
              folder.

version       Simple text string denoting the version of the package.  Note
              that if you with you update your plugin in the repository this
              field HAS to be different than the any previous versions.
              
author        The plugin author's name goes here.  can be anything really. ;)
              
description   A text field that allows the developer to say a few words about
              what the plugin does.  It is recommended to keep this short as
              this will be displayed when the user searches for plugins.  Also
              due to limitations of json, this has to be on 1 line.  you can
              add line breaks with \n however.

website       Whats the plugin homepage?
              
bukkit_min    The minimum build number that this plugin supports. Must be
              larger than 0.  Keep in mind that this is used to present
              plugins that the user is able to run with their current bukkit
              binary that they installed.
              
bukkit_max    The maximum build number that the plugin supports.  Must be
              larger than the minimum.  Keep in mind that this is used to 
              present plugins that the user is able to run with their current 
              bukkit binary that they installed.
              
depoendencies This is a list (by name) of any packages that the plugin is
              dependent on in order to run.  These plugins need to be
              installed in order to make your plugin work.

categories    A list of categories that the plugin falls under.  Use the
              standard set int he forum for this use.  Also if there are
              multiple categories, list all of them and do not use notation
              like GEN/SEC as that will pollute the categories field with a
              bunch of junk.