BukGet Packaging Howto
----------------------
Here are some general tips and information.

1) All BukGet Packages are Zip files.

2) BukGet Packages are required to have plugins, lib, and etc folders in the
   package root.  These folder can be empty, however are needed in order to
   pass the check.

3) There must be at least 1 jar file within the package.  If there is no java
   binary then what are you generating a package for? :-p

4) It is preferable to package in any libraries you may need into the package.
   if you would prefer to alternatively package the libraries separately, make
   sure that the library doesn't already exist in the repository.

5) The jar file must match the name of the package (including case).  This
   will be checked in both the lib and plugins folder.  One of these locations
   must have a match.

6) Repository regeneration will happen every hour.  So on a worst-case
   scenario, you should see your package added to the repository within the
   next hour.

LAYOUT:
-------

/plugins/
/lib/
/etc/


How to generate your first package:
-----------------------------------
This is a basic how-to in order to walk a developer through generating their
first package and submitting it to bukget to be included into the canonical
repository.

1) Create a folder named "package".

2) Create 3 folders named "plugins", "lib", and "etc" within the "package"
   folder.

3) Place your plugin binary in the "plugins" folder.  Any information in this
   location will be automatically overwritten on upgrades, so it is not
   recommended to put any config files in here.

4) Place any configuration information you want to be dropped into a new
   installation into the "etc" folder.  Any files that exist here will first 
   be checked to see if they exist before being dropped in.
  
5) Any libraries that you need should be placed in the "lib" folder.  Just as
   with the "etc" folder if a library exists it will not be overwritten.

6) Zip up all of the contents of the "package" folder so that the package
   folder does not exist in the zip file.  For example, if this is done
   properly when you unzip the package there should not be a "package" folder
   being generated.
   
7) Generate an MD5 Sum of the zip file.  This will be put into the dictionary
   so that the package client knows that it downloaded a complete package.

8) Take a copy of the example_info.json file and fill out the needed
   information.  Take care to make sure that the package name matches the
   name of the jar file in the plugins folder (or the lib folder if this is a
   library package).  This does include case sensitivity.  Also make sure to
   strip out any extra versioning items as they will will just pollute the
   repository.

9) Upload both the json file and the zip package to your site, dropbox, or
   github repository.  All of the uploads must however be directly
   downloadable.  This means that sites like Megaupload will not work.

10) Fill out the form on http://bukget/add with all the requested information,
    including the location of the json file.  A verification email will then
    be sent to verify that your email address is valid and then the an
    activation request will be sent to your bukkit.org address to make sure
    you are who you say you are.  Lastly your name will be checked against the
    plugin forum to make sure you's username really did write the package.  If
    all of these checks pass, then your plugin dictionary will be added to the
    canonical repository that the clients will use to pull the packages.

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
              
dependencies  This is a list (by name) of any packages that the plugin is
              dependent on in order to run.  These plugins need to be
              installed in order to make your plugin work.  If there are no
              dependencies then an empty list [] must be used.

categories    A list of categories that the plugin falls under.  Use the
              standard set int he forum for this use.  Also if there are
              multiple categories, list all of them and do not use notation
              like GEN/SEC as that will pollute the categories field with a
              bunch of junk.