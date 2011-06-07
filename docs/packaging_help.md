Packaging
=========

Packaging for BukGet can be as simple or as complex as you need.  The basic premise for getting a package included into BukGet remains the same. This document will walk you through setting up your Bukkit plugin to be distributed through BukGet with minimal mess.  Before we start, lets talk about the requirements:

* Plugin developers host their own packages.  We do not host the packages, only provide a mechanism by which to find and download them.  Please keep this in mind as we handle the repository in this manner to provide both the maximum amount of flexibility to the plugin developer and to try to keep our own colocation costs to a minimum.
* File hosting services that do not provide direct links will not work.  This means that hosting services such as MegaUpload will not work since there is no way for the BukGet backend or the BukGet client to pull any of the data that you upload to these sites.  The hosting service you are using must not change the URL of files if they are updated.  BukGet uses a static location to pull your plugin dictionary.  If the URL changes, the backend can no longer track your package and it will be orphaned.  Services that are ok to use include (but aren't limited to) the following:
  * Dropbox
  * CloudShare
  * SugarSync
  * Github
* The use of URL Shorteners is not recommended.  Some shorteners will redirect the URL in a way that will break our retrieval mechanisms.  As the URLs for both the plugin dictionary and the plugins packages themselves will not be used directly by users, these don't have to be pretty, just directly linkable.
* BukGet checks your plugin against the plugins.bukkit.org database.  If your plugin is not listed there, then there is no way for us to validate that you are the developer.  Please go through Bukkit's normal submission process before submitting to BukGet.

Getting Started with Packaging Manually
---------------------------------------

For the sake of argument, lets say you have a simple Bukkit plugin that does not require manually placing a configuration file and does not depend on any other plugins.  In many cases this is one of the most common types of plugins available for Bukkit and is also the easiest to package for BukGet.

Our first task is to get the md5sum of the plugin.  Depending on what OS you use the method will vary:
* Max OSX
  * Open the Terminal.app
  * type: md5 /path/to/plugin.jar
  * You should get a response similar to below.  The md5 hash is everything
    after the equals sign.
    `MD5 (plugin.jar) = 9d92a8d4190944cf075c8ecdd56788e8`
* Linux
  * Open a Terminal
  * type: md5sum /path/to/plugin.jar
  * You should get a response similar to below.  The md5 hash is the string
    before the filename.
    `9d92a8d4190944cf075c8ecdd56788e8 /path/to/plugin.jar`
* Windows
  * Download one of any number of tools out there to generate md5 sums.  Some
    that have been recommended by other plugin developers are 
    [Graphical MD5Sum][md51] and [MD5Summer][md52].

The second step is to upload the plugin.jar file somewhere and get its URL. we will need this to generate the plugin dictionary.  Depending on how you are hosting your plugin this can be handled any number of ways and is beyond the scope of this document.

Our next step is to generate the plugin dictionary.  For this example all we really need is a skeleton dictionary that can tell BukGet what the plugin is and where we can find it.

`{
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
        "location": "http://www.website.com/location/to/zipfile.zip",
        "checksum": "MD5-CHECKSUM-GOES-HERE",
        "branch": "stable",
        "engines": [{
          "engine": "craftbukkit",
          "build_min": 800,
          "build_max": 900
        }]
    }]
}`
For information about what each of these fields are, please review the definitions in README.md.

Once you have the dictionary filled out, save the file, upload it to your hosting solution, and get the URL.  Once you have the URL, simply go to the [bukget.org][BukGet] website and fill out the "Add Plugin" page with the URL of the plugin dictionary.  After you submit, the BukGet server will try to validate the information you sent us with what is available on the [Bukkit plugins list][b_plugs] page.  Within a few minutes, the server will send a private message to your [bukkit.org][Bukkit] account with an activation link.  Once you click on the link, your new entry will be considered active and will be added to the repository dictionary the next time it is generated.

[b_plugs]:  http://plugins.bukkit.org
[bukget]:   http://bukget.org
[md51]:     http://www.toast442.org/md5/
[md52]:     http://www.md5summer.org/