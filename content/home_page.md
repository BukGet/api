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

## I want to run a child server, how do i? ##
Download the code and set it up as per the installation instructions in the
[GitHub][github] Readme file.  If you wish to host publicly, simply contact
me at steve \_at\_ chigeek.com for inclusion.

We need child servers to help distribute the load.  Over the month of January
there were over 1.2 million API calls to the grand parent server and that
number is expected to grow.

##<a name="api" /> Geeky API Stuff </a>##
For API information, please refer to the [GitHub code][github] repository.

[dbo]: http://dev.bukkit.org
[github]: https://github.com/SteveMcGrath/bukget