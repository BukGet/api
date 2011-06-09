Packaging
=========

Packaging for BukGet can be as simple or as complex as you need.  The basic premise for getting a package included in BukGet remains the same. This document will walk you through setting up your Bukkit plugin to be distributed through BukGet with minimal mess.  Before we start, lets talk about the requirements:

* Plugin developers host their own packages.  We do not host the packages, only provide a mechanism by which to find and download them.  Please keep this in mind as we handle the repository in this manner to provide both the maximum amount of flexibility to the plugin developer and to try to keep our own colocation costs to a minimum.
* File hosting services that do not provide direct links will not work.  This means that hosting services such as MegaUpload will not work as there is no way for the BukGet backend or the BukGet client to pull any of the data that you upload to these sites.  The hosting service you are using must not change the URL of files if they are updated because BukGet uses a static location to pull your plugin dictionary.  If the URL changes, the backend can no longer track your package and it will be orphaned.  Services that are ok to use include (but aren't limited to) the following:
  * Dropbox
  * CloudShare
  * SugarSync
  * Github
* The use of URL shorteners is not recommended.  Some shorteners will redirect the URL in a way that will break our retrieval mechanisms.  As the URLs for both the plugin dictionary and the plugin packages themselves will not be used directly by users, these don't have to be pretty, just directly linkable.
* BukGet checks your plugin against the plugins.bukkit.org database.  If your plugin is not listed there, then there is no way for us to validate that you are the developer.  Please go through Bukkit's normal submission process before submitting to BukGet.

Getting Started with Packaging Manually
---------------------------------------

One of the most common cases is a simple Bukkit plugin with no configuration file or an automatically generated one that does not depend on any other plugins.  This is very easy to package for BukGet.

Our first task is to get the md5sum of the plugin.  The steps vary by OS:

* Max OSX
  1. Open the Terminal.app
  2. type: md5 /path/to/plugin.jar
  3. You should get a response similar to below.  The md5 hash is everything
    after the equals sign.
    `MD5 (plugin.jar) = 9d92a8d4190944cf075c8ecdd56788e8`
* Linux
  1. Open a Terminal
  2. type: md5sum /path/to/plugin.jar
  3. You should get a response similar to below.  The md5 hash is the string
    before the filename.
    `9d92a8d4190944cf075c8ecdd56788e8 /path/to/plugin.jar`
* Windows
  * Download one of any number of tools out there to generate md5 sums.  Some
    that have been recommended by other plugin developers are 
    [Graphical MD5Sum][md51] and [MD5Summer][md52].

The second step will be to upload the plugin.jar file somewhere and get its URL.  We will need this to generate the plugin dictionary.  Depending on how you are hosting your plugin this can be handled any number of ways and is beyond the scope of this document.

Our next step is to generate the plugin dictionary.  For this example all we really need is a skeleton dictionary that can tell BukGet what the plugin is and where we can find it.

<pre class="brush: js">
  {
    "name": "PackageName",
    "authors": ["Author1"],
    "maintainer": "Author1",
    "description": "Some details about what the plugin does.  If you want a line break use \n.",
    "website": "http://www.website.com",
    "categories": ["GEN", "ADMN"],
    "versions": [{
      "version": "0.0.1a",
      "required_dependencies": [],
      "optional_dependencies": [],
      "conflicts": [],
      "location": "http://www.website.com/location/to/jarfile.jar",
      "checksum": "MD5-CHECKSUM-GOES-HERE",
      "branch": "stable",
      "engines": [{
        "engine": "craftbukkit",
        "build_min": 800,
        "build_max": 900
      }]
    }]
  }
</pre>

For additional information about what each of these fields are, please review the definitions at the end of this document.

Once you have the dictionary filled out, save the file, upload it to your hosting solution, and get the URL.  Once you have the URL, go to the [bukget.org][BukGet] website and fill out the "Add Plugin" page with the URL of the plugin dictionary.  After you submit, the BukGet server will try to validate the information you sent us with what is available on the [Bukkit plugins list][b_plugs] page.  Within a few minutes the server will send a private message to your [bukkit.org][Bukkit] account with an activation link.  Once you click on the link, your new entry will be considered active and will be added to the repository dictionary when it is next generated.

[b_plugs]:  http://plugins.bukkit.org
[BukGet]:   http://bukget.org
[md51]:     http://www.toast442.org/md5/
[md52]:     http://www.md5summer.org/

Building Compliant Zip Packages Manually
----------------------------------------

Not all plugins can be distributed as a single jar file.  Some plugins rely on other libraries or have configuration files.  For these plugins there is a simple format for generating a plugin package for BukGet using a Zip container.  The Zip folder layout is described below:

<pre class="brush: bash">
    /lib
    /plugins
    /plugins/PLUGINNAME
</pre>

* **/lib**: This folder contains any external libraries Bukkit must load.  SQL libraries go here.
* **/plugins**: This folder contains your plugin.  Files in this location WILL be overwritten when a package is updated.
* **/plugins/PLUGINNAME**: This folder contains any configuration files or other files your plugin requires. Files in this location will NOT be overwritten.

There are no dictionaries stored in the package itself.  BukGet relies on these to identify packages.  Simply replace the jarfile in the above instructions with your zip package.

Plugin Dictionary Definitions
-----------------------------

**name**

  * *Type*: Unicode String
  * *Description*: The package name.  This field must not have any spaces, must match the name used for packaging and in the Bukkit forums.

**authors**

  * *Type*: List of Unicode Strings
  * *Description*: List of all the author names for the plugin.

**maintainer**

  * *Type*: Unicode String
  * *Description*: This is name of the user that is maintaining the plugin.  This name must be a valid Bukkit.org account and must also be the same name as the one who had started the forum thread on the Bukkit forums.

**description**

  * *Type*: Unicode String
  * *Description*: A brief description of what the plugin is, what it does, and maybe even how to use it.

**website**

  * *Type*: Unicode String
  * *Description*: The URL of the plugin homepage or forum thread.

**categories**

  * *Type*: List of Unicode Strings
  * *Description*: List of the categories the plugin falls under.  This should match what is on for Bukkit forum page.  Please note that we are requesting that you submit each catagory as an item in the string.  The categories should not be formatted like `GEN/ADMN/FUN` but should instead be `['GEN','ADMN','FUN']`.

**versions**

  * *Type*: List of Version Dictionaries
  * *Description*: This is a container for all version objects.

**version**

  * *Type*: Unicode String
  * *Description*: Version number of the plugin.

**required_dependencies**

  * *Type*: Nested List of Unicode Strings
  * *Description*: A list of the required plugin dependencies needed to make your plugin work.  Typically this should be a simple list of plugin names that are needed to make the plugin work.  There is one addition however; if you need to specify one plugin OR another, then set them within their own list.  For example: If you need Permissions or GroupManager, then instead of listing them both at the base list, nest them as their own list. In this example:  `[["Permissions","GroupManager"], "Help"]` we need Help and either Permissions or GroupManager.

**optional_dependencies**

  * *Type*: Nested List of Unicode Strings
  * *Description*: Same as required_dependencies, however these items aren't required for the plugin to run and can only enhance functionality.

**conflicts**

  * *Type*: List of Unicode Strings
  * *Destription*: A list of Plugins that conflict with this version of your plugin.

**location**

  * *Type*: Unicode String
  * *Description*: The URL to this version of your plugin or plugin package.

**checksum**

  * *Type*: Unicode String
  * *Description*: The MD5 checksum of the plugin or package.  This is used to validate that the package the client download is the right package and is not corrupt.

**branch**

  * *Type*: Unicode String
  * *Description*: Denotes the status of the plugin version.  The allowed values for this field are *stable*, *test*, and *dev*.  Plugin versions with the *dev* tag are to be considered development works-in-progress and no stability should be expected of them.  Plugin versions with *stable* are considered to be stable plugins with relatively few known bugs.  The *test* tag is an intermediate between *dev* and *stable*.

**engines**

  * *Type*: List of engine Dictionaries
  * *Description*: This is a container for all the engine specifications.  This was added late in the spec to account for the possibility of alternative server builds to the craftbukkit server.  Notable works-in-progress here include the Glowstone server.

**engine**

  * *Type*: Unicode String
  * *Description*: Denotes what engine the build restrictions pertain to.  Currently the only value accepted here is *craftbukkit*.

**build_min**

  * *Type*: Integer
  * *Description*: The minimum build number that this plugin will work with for this engine.

**build_max**

  * *Type*: Integer
  * *Description*: The maximum build number that this plugin will work with for this engine.

Expanded Example JSON Dictionary
--------------------------------

<pre class="brush: js">
  {
    "name": "PackageName",
    "authors": ["Author1"],
    "maintainer": "Author1",
    "description": "Some details about what the plugin does.  If you want a line break use \n.",
    "website": "http://www.website.com",
    "categories": ["GEN", "ADMN"],
    "versions": [{
      "version": "0.0.1b",
      "required_dependencies": [["Permissions","GroupManager"],"Help"],
      "optional_dependencies": [],
      "conflicts": [],
      "location": "http://www.website.com/location/to/zipfile.zip",
      "checksum": "MD5-CHECKSUM-GOES-HERE",
      "branch": "stable",
      "engines": [{
        "engine": "craftbukkit",
        "build_min": 817,
        "build_max": 900
      }, {
        "engine": "glowstone",
        "build_min": 0,
        "build_max": 0
      }]
    },   {
      "version": "0.0.1a",
      "required_dependencies": ["Help"],
      "optional_dependencies": [],
      "conflicts": [],
      "location": "http://www.website.com/location/to/zipfile-0.0.1a.zip",
      "checksum": "MD5-CHECKSUM-GOES-HERE",
      "branch": "test",
      "engines": [{
        "engine": "craftbukkit",
        "build_min": 740,
        "build_max": 806
      }]
	}]
  }
</pre>