BukGet Backend dev2 Goes Live
-----------------------------
*June 09, 2011*

Dev2, a complete recode of the backend systems, is now the primary site for BukGet.  This signals a departure from using a hodgepodge of languages, tools, and technologies as all of the backend code is now written in python using Bottle and SQLAlchemy.  This allows for a lot of flexibility as well, as bottle opens us up to performing upgrades to the code in a faster, more flexible, and more gradual way.  This means that overall the code is easier to maintain as well, so we can respond to issues more quickly.

As this is a new site, and since there have been some significant changes to the plugin.json format, we are asking all current plugin devs to re-submit their plugins through the new site.


BukGet Backend Redesign Underway
--------------------------------
*May 31, 2011*

After a short break from working on BukGet to get a new perspective and a long vacation, a couple of us looked at the current code and it was decided that the BukGet backend should be in 1 language (vs. 2 currently) and should be integrated instead of all over the place.  So I started working on moving the site over to python using bottle and tying that into the current python batch scripts.  Ideally most of the batch processing will then go away so updates can happen more frequently.


BukGet Repository Testing has started!
--------------------------------------
*May 05, 2011*

With some help from the community we should be able to start accepting plugin submissions soon. I expect there to be many bugs and issues to work out, however hopefully by the end of the week most of the issues should be ironed out. as it sits currently, here is the submission process:

Follow the plugin repository guidelines:

* Submit the repository URL to bukget
* BukGet will check to make sure that there is a forum post of the plugin
* BukGet will check to make sure you are the author of the plugin
* BukGet within 5 minutes if all checks are good you will be sent a PM on the bukkit.org forums to validate you are who you say you are.
* You will need to click the link sent to validate you are who you say you are.
* BukGet will activate the entry on our side.
* BukGet will on an hourly basis check all the plugin repository URLs, validate that they are properly formatted and then add them to the repository.

At this stage I don't see this process changing much. If something does change I will make sure to inform everyone. However progress is being made!
Tags: server, python, php, website


BukGet Client Released!
-----------------------
*May 04, 2011*

The first build of the bukget is now available! This first version does have a lot of non-working parts, however they should all be labeled as such in the help documentation. I am still working on getting the help page online to help support the code, however I think that for the time being that current code should should be able to support itself.

Getting started:

* The current version REQUIRES Python 2.6.0 or better. If you are running a CentOS 5 or RHEL5 host, read the following instructions:
  1. run: `wget http://download.fedoraproject.org/pub/epel/5/i386/epel-release-5-4.noarch.rpm`
  2. run: `rpm -ivh epel-release-5-4.noarch.rpm`
  3. run: `yum -y install python26`
1. Download the latest bukget release here.
2. move the file into the location you want to run your minecraft server.
3. gunzip the file and set the execute bit on the client.
4. If bukget throws a warning, install the requested packages.
5. run `./bukget bukkit upgrade`
6. run `./bukget bukkit start`
7. And you up and running.

Launching Interactive Mode:

* `./bukget`

Getting help:

* Command line: `./bukget help [command]`
* Interactive: `help [command]`

TODO & Bugs:

* Check for java and screen and offer to install if possible (CentOS/Fedora and Debian/Ubuntu)
* Check if folder structure exists and offer to prepare automatically
* Fix player list
* Write Snapshot
* Intro text should mention the help command
* bukkit configuration command needs to be written
* Commands should present more output to the user
* pkg command set completely unwritten
* Need to clean up code.
* Code needs to be documented better.


BukGet Entering Alpha State
---------------------------
*May 02, 2011*

After a few revisions and rewrites, we are almost ready to enter an alpha state. While there is still a long way to go from here and I'm sure there will be more than a few bugs to work out, I think we are at the point where we need to reach out to the community to try to get some input and support to continue this project. As a result of that, we are asking everyone for any comments, concerns, help, and input in order to help bring this project to fruition.

**Client Status:**
The bukget client is in a run-able state as it sits for Linux and Mac OSX. Currently it will not attach to any plugin repositories so it only has the capability to update bukkit and start and stop it. In order to be able to background the server, we are interacting with screen to handle these actions.

**Server Status:**
The server version 0.0.1a was written and is already being used as a basis for 0.0.2. Because of the change in direction from a centralized repository (ala apt-get) to something more akin to python's setuptools or perl's CPAN, a complete rewrite is needed. As a result of that, we currently do not have any code in place to generate the repository, however we DO need developers to start using the format laid out in the help section in order to get a base set to work with. The goal is to have a working repository system up and running before June.

**Website Status:**
I know some people have commended on the bare site currently. Most of my focus has been on coding the client and server and not on getting this site up and running. As a result of that many of the pages are either only half-complete or not functioning all-together. My plan is to have all of this rectified however somewhat shortly.