##<a name="main"> What is BukGet? </a>##
BukGet is a API into [dev.bukkit.org][dbo] that
is trying to parse out the relevant details needed to perform package
management for Bukkit.  We do not have a client that interacts with our API,
however instead offer the API to anyone wishing to use it to build their own
package management system for Bukkit.  We do our best to try to parse out all
of the relevant data, including dependencies, CB build numbers, etc. to help
aide developers along in getting the information they need.

## How do I use BukGet? ##
We have a JSON API that you can interact with in order to pull the information
you need.  Details on how to interact with the API are explained later on in
this document.

## How do I get my plugin included in BukGet? ##
Is your plugin in [dev.bukkit.org][dbo]?  If it is, then your plugin is
already included.
  
##<a name="api" /> Geeky API Stuff </a>##
The API was specifically written to handle just about everything as GET 
requests.  This makes is easier to interface with in many languages as you 
don't need to worry about any header information like Content-Length and url 
encoding.  Generation cycles run every 6 hrs so the information in the API 
can be no more than 6hrs behind [dev.bukkit.org][dbo].  The only things that
you should be aware of is that when generating URLs spaces are converted to
underscores.  So for example when performing a category breakdown for
"Admin Tools", you would use the URL of: /api/category/Admin_Tools

### API Generation Information Page ###
_/api/_

    { "changes": [ { "plugin": "PLUGINNAME", "version": "VERSION" }, 
                   { "plugin": "PLUGINNAME", "version": "VERSION" }], 
     "date": 1323047181, 
     "duration": 4950, 
     "id": 3 
    }

* Changes: List of Dictionaries with the names and versions of the plugins
           that were updated in the last generation cycle.
* Date: The timestamp that the generation completed.
* Duration: The amount of time it took to run the regen in seconds.
* ID: The Generation ID.  This gets incremented by 1 every generation.

### Plugin List ###
_/api/plugins_

    [
        "PLUGINNAME1", 
        "PLUGINNAME2", 
        "PLUGINNAME3", 
        "PLUGINNAME4",
    ]

Produces a complete list of all of the plugins int he database.

### Plugin Details ###
_/api/plugin/:PLUGINNAME_

    {
        "authors": ["AUTHOR"], 
        "bukkitdev_link": "http://dev.bukkit.org/server-mods/PLUGINNAME/", 
        "categories": ["CATEGORY1", "CATEGORY2"], 
        "name": "PLUGINNAME", 
        "status": "RELEASE STATUS", 
        "versions": [
            {
                "date": 1317404619, 
                "dl_link": "http://dev.bukkit.org/media/files/LINK_TO_JAR/ZIP", 
                "filename": "AcceptRules.jar", 
                "game_builds": ["1000", "9999"], 
                "hard_dependencies": [], 
                "md5": "8184a10ef2657024ca0ceb38f9b681eb", 
                "name": "v0.7", 
                "soft_dependencies": []
            }
        ]
    }

#### Plugin Definitions ####
* Authors: List of authors on the plugin
* BukkitDev_Link: Link to the plugin's page on DBO
* Categories: List of categories that the plugin is associated with
* Name: Name of the plugin
* Status: The release status of the plugin
* Versions: List of version dictionaries detailing the various versions of the
            plugin

#### Version Definitions ####
* Date: Timestamp that the version was uploaded
* DL_Link: URL to the JAR/ZIP file
* FileName: The filename of the JAR/ZIP file
* Game_Builds: List of compatible builds the plugin will run on
* Hard_Dependencies: List of dependent plugins needed for the plugin to run
* Soft_Dependencies: List of plugins that this plugin can hook into
* MD5: The MD5 sum of the JAR/ZIP file
* Name: The version name

### Category List ####
_/api/categories_

    [
        "CATEGORY1", 
        "CATEGORY2"
    ]

Returns a list of the available categories in the database.

### Category Breakdown ###
_/api/category/:CATEGORY_

Provides a list of plugins just like /api/plugins, however this list is
limited to just the plugins that are tagged with the given category.

### Searching [BETA] ###
_POST: /api/search_

NOTE: The ability to generically search the database exists, however is not
extensively tested.  If there are any issues or bugs related to this function,
please let me know.

Here you should be able to search based on a single field in the database.
This is done my sending a POST request to the URL with the following 3 fields
set in a url-encoded format.

* field_name: Here we specify the field name that we will be searching
              against.  You can search based on any of the fields in the
              plugin or versions dictionaries.  If the field is in the 
              versions dictionary, then you will need to prepend the field
              name with v_ so that the server knows what it's searching for.
* action: Specifies the action you with to perform against the value specified.
  * =: Equals
  * <: Less Than
  * >: Greater Than
  * <=: Less Than or Equal To
  * >=: Greater Than or Equal To
  * in: Is value in the field_name's list?
  * like: Partial matching.
* value: The value you are performing the action against.

### Full Index ###
_/api/json_

This url will output the entire in-memory plugin list.  The format will be a
list of plugin objects.  This is easily over 1-2MB in size and may take some
time to download properly.


[dbo]: http://dev.bukkit.org