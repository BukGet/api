## BukGet ##
BukGet is a JSON API into dev.bukkit.org.  The idea is to provide some sort of
an interface into DBO's contents as Curse doesn't natively have one for us to
interact with.

## Installation and Configuration ##
BukGet is designed to run both inside and outside of a python virtualenv.
While not required, we highly recommend that you use a virtualenv as it
creates a virtual python environment for bukget to run within that doesn't
create issues with the global site packages.

Running a child server is very beneficial to the service as it allows us to
offload some of the requests to a potentially more local server.  If you are
interested in running a public child server, please contact me.

### Package Dependencies ###

* SQLAlchemy
* Bottle
* PyYAML
* Markdown2
* Twisted or alternative Bottle supported web service.

### How to Install ###

**Basic**

* Install Python and Python-Dev as needed for your OS/Distrobution.
* Download and Install VirtualEnv
* Clone the repository
* Copy the bukget_example.ini file to bukget.ini and configure as needed.
* Run the server.py script to start the server up.

**Expanded**

The following instructions are assuming that CentOS 6 is installed:

1. The first thing we need to do is update the system as needed and install 
   the needed OS packages.
    * `yum -y update`
    * `yum -y groupinstall 'Development Tools'`
    * `yum -y install python-devel python-setuptools git`

2. Next we need to install virtualenv and build the environment to support
   bukget.
    * `easy_install virtualenv`
    * `mkdir -p /opt/bukget/code`
    * `virtualenv --no-site-packages /opt/bukget`
    * `source /opt/bukget/bin/activate`
    * `pip install sqlalchemy bottle pyyaml markdown2 twisted`

3. Lastly we need to download the BukGet code, configure it, and run it.
    * `git clone git://github.com/SteveMcGrath/bukget.git /opt/bukget/code`
    * `cp /opt/bukget/code/bukget_example.ini /opt/bukget/code/bukget.ini`
    * `vi /opt/bukget/code/bukget.ini`
    * `/opt/bukget/code/server.py`

## API Calls ##
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
        "desc": "This is the first 200 chars of the description on DBO..."
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
                "soft_dependencies": [],
                "status": "Semi-Normal",
                "type": "Release"
            }
        ]
    }

#### Plugin Definitions ####
* Authors: List of authors on the plugin
* BukkitDev_Link: Link to the plugin's page on DBO
* Categories: List of categories that the plugin is associated with
* Name: Name of the plugin
* Desc: The first 200 Characters of the description page contents on DBO.
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
* Status: This is the status of the plugin as defined by Curse
* Type: The release type that the developer assigned to the plugin.  This can
        be any number of statuses from Alpha, Beta, Release, etc.

### Plugin Details: Specific Version ###
_/api/plugin/:PLUGINNAME/:VERSION_<br />
_/api/plugin/:PLUGINNAME/latest_

A convenience function to only show the specified version in the versions
list.  If "latest" is used instead of a version name, the latest plugin by
date uploaded will be presented.

### Plugin Download ###
_/api/plugin/:PLUGINNAME/:VERSION/download_<br />
_/api/plugin/:PLUGINNAME/latest/download_

A convenience function that will redirect to the file for the specified 
version of the specified plugin for download.  The download mechanism must
support redirects in order to use this function.

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

### Searching ###
_POST: /api/search_<br />
_GET: /api/search/:FIELD/:ACTION/:VALUE_

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

### Full Index, Latest Versions Only ###
_/api/json/latest_

This url is a convenience function of the full json that will only ever return
the most recent version.

### Offline DB Cache ###
_/api/cache_

Returns a sqlite DB with the full contents of the JSON file.  Created to help
cope with the large size of the JSON format and the long wait times people
were experiencing with Java.

[dbo]: http://dev.bukkit.org