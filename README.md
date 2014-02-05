## BukGet
BukGet is a JSON API into dev.bukkit.org.  The idea is to provide some sort of
an interface into DBO's contents as Curse doesn't natively have one for us to
interact with.

### What does it do?
BukGet is a API into [dev.bukkit.org][dbo] that
is trying to parse out the relevant details needed to perform package
management for Bukkit.  We do not have a client that interacts with our API,
however instead offer the API to anyone wishing to use it to build their own
package management system for Bukkit.  We do our best to try to parse out all
of the relevant data, including dependencies, CB build numbers, etc. to help
aide developers along in getting the information they need.

### How do I use BukGet?
We have a JSON API that you can interact with in order to pull the information
you need.  Details on how to interact with the API are explained later on in
this document.

### How do I get my plugin included in BukGet?
Is your plugin in [dev.bukkit.org][dbo]?  If it is, then your plugin is
already included.


### Where can I get more information?

Visit the Projects main website [bukget.org][bukget]

[bukget]: http://bukget.org
[dbo]: http://dev.bukkit.org

## Arch Overview

BukGet utilizes MongoDB as the back-end database and is coded using the bottlepy web framework.  For scalability, we use Paste as the application server and front-end that with Nginx for URL routing (in-case we need to stand up a dev instance) as well a logging all of the requests.  This implementation framework has been able to handle 20M requests a month without showing any significant impact on the hardware (~10% CPU Utilization and ~1-2% I/OWait as of the writing of this document).

__Application List__

* MongoDB
* Python 2.6/7
* Bottle
* Tornado
* Nginx

__Script List__

* bukgen_bukkit
* bukgen_manual
* bukget
* force_update.py
* logreader.py

__Services List__

* nginx - sysv
* mongod - sysv
* bukget - upstart


__Services Layout (By Server)__

* dallas.api.bukget.org
    * BukGet API (Nginx, Mongo, BukGet)
    * logreader script (cronjob)
    * BukGen Generator (bukgen_* applications)
    * Maintinence Functions (force_update.py, bukgen_manual)
* paris.api.bukget.org
    * BukGet API (Nginx, Mongo, BukGet)
* dev.vpn.bukget.org
    * Development Services (Independent of Prod)
        * BukGet API (Nginx, Mongo, BukGet)
    * Production Database Nightly Backup


### MongoDB

The Mongo Database has not had any customization that needs to be documented at this time.  The Dallas server is the primary database engine, with the Paris server acting as the secondary.  This means that all Database writes has to go through the Dallas Mongo instance.


### Python 2.6/7

The Python Installation on the server(s) is the default installation that comes with CentOS 6.3 x64.  Pip has also been installed on these hosts manually and is being used to help manage the installation of any needed dependencies as well as the installation of the bukget and bukgen packages themselves.  These packages are being pulled directly from the git repository and then being updated using the following command in the appropriate directory:

`pip install --upgrade ./`

This will install/upgrade any dependencies for the package as well as install the latest version of the package itself.


### Nginx

Below is the configuration for the VHost that we use for BukGet.  Keep in mind that minor modifications may exist to also listen for the hostname as well as api.bukget.org

    server {
            listen          80;
            server_name     api.bukget.org XXX.api.bukget.org;

            access_log      /var/log/bukget/api-access.log;
            error_log       /var/log/bukget/api-error.log;

            location / {
                    proxy_pass              http://127.0.0.1:9132/;
                    proxy_redirect          off;

                    proxy_set_header                Host            $host;
                    proxy_set_header                X-Real-IP       $remote_addr;
                    proxy_set_header                X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_max_temp_file_size        0;

                    client_max_body_size            10m;
                    client_body_buffer_size         128k;

                    proxy_connect_timeout           90;
                    proxy_send_timeout              90;
                    proxy_read_timeout              90;

                    proxy_buffer_size               4k;
                    proxy_buffers                   4 32k;
                    proxy_busy_buffers_size         64k;
                    proxy_temp_file_write_size      64k;
            }
    }


### bukgen_bukkit Script

This script is the main script that is being run to keep bukget up to date.  This script runs every 6 hours.  It can also be run manually as needed (uncommon).  The script has a self-imposed 2 second delay for each URL request so not to overwhelm BukkitDev.  It's still worth noting that if a generation is run outside of the normal window, to check to make sure nothing else is currently talking to BukkitDev so now to overwhelm the service we're pulling from.

BukGen also has a number of built-in safeties aside from the 2 second delay.  These mechanisms have evolved over the life of the generation script and may change:

* __2 Second Delay Timer__: Delays the amount of time globally for each request to BukkitDev.  This is tunable.
* __Re-pull URL on Failure__: The system will automatically dwell on URLs that have failed to pull (i.e. timeout has been reached).  This allows the generation script to effectively pull the required data.
* __Stop Pulling Bad Data After 3 Re-trys__: If the generator receives an HTTP code other than a 200-OK (timeouts excluded) then it will attempt another 2 times.  If a 200-OK is not returned, then it will fail the URL out and continue on.  This prevents the generator from going into an infinite request loop.

__Options__

* __speedy__: This is the normal run behavior.  It will run through BukkitDev until it no longer finds any updates to process, then terminates.
* __full__: This process will run through all of BukkitDev, ignoring any existing data and will update everything.  This is generally only used when API changes of DB re-population is needed.  This will take several days to complete.
* __speedy_full__: Forces bukgen to look at every plugin, however will still honor any existing data for each plugin.  This function effectively replaces the stage_update function and is designed to be run monthly to update any stale information about the plugin itself.
* __stage_update__: Function to only update the stage value for the plugin.  Rotates through all plugins in the database and will mark any deleted plugins as well as update the stage of the plugin.


### bukgen_manual Script

This is a script to manually update the document to one or many plugins.  There may be many reasons for doing this, however this generally relates to the generator script not being able to pull the right data (this is most common with plugins that are bundled in zip files).  To run the script, first you will need to create a json file with the corrected plugin definition and place it into the directory `/tmp/bukget/fixed_json`.  You may need to create this directory if it doesn't exist.  The filename of the json files are not important, however they must have the .json extension and be only 1 plugin per json file.  When ready, just run the command `bukkit_manual`.  The script should import/update the given plugins then remove the .json files as it runs.


### bukget Script

This is the bukget api launcher script.  This is generally run from the upstart job, however can be manually run when debugging code to see what the errors are.


### force_update.py script

This script will update the plugins specified as arguments out-of-band of the normal update cycle.  This is useful when a plugin either was never updated, or the update never completed for this plugin.  These occurrences are rare, however do happen from time to time.

#### Usage:

`/opt/bukget/devfiles/force_update.py plugin_name_1 plugin_name_2`


### logreader.py Script

This script is designed to run nightly from a cronjob.  It walks through the previous days nginx log, determines how many calls to each plugin and from each API were performed, then also updates the popularity scoring based on those.  It is not recommended to run this script outside the normal schedule unless it fails as it will modify the popularity scoring for all plugins in the system.