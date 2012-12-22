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