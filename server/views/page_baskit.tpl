<h2>Baskit, the Bukkit Server Manager</h2>
<p>
  Baskit is an open source management tool for bukkit servers.  Baskit is
  designed to handle most of the basic functions for minecraft/bukkit server
  administrators.  These functions include:
  <ul>
    <li>Backgrounding the server without any complexities.</li>
    <li>Automating Backups for worlds.</li>
    <li>Providing a safe way to roll back plugin or bukkit updates.</li>
    <li>Provide a simple and effective way to script more complicated actions.</li>
    <li>Handle downloading and installing the bukkit server</li>
  </ul>
</p>
<p><img src="/static/images/baskit.png" /></p>
<p>
  Baskit was originally part of the Bukget package menagement system, however
  with Nijikokun developing the packaging parts as a bukkit plugin, it was
  decided to rethink the future of the wrapper.  The result is an extremely
  scaled down and lightweight tool for managing your bukkit server.  With
  Baskit, you can easily manage the mundane aspect of your bukkit server and
  spend more time in the game instead.
</p>
<p>
  <strong>Snapshots:</strong>  The premise of snapshots is to create a
  point-in-time backup of your running configuration, including the bukkit
  binary, any plugins, and their configurations.  Snapshots do NOT contain
  any world data and therefore are fairly small in size.  Where snapshots
  really become useful is in creating "restore points" with known working
  configurations before you update the bukkit binary or any of the plugins,
  add new plugins, or remove anything.  If anything goes wrong, it's really
  simple to restore back to that known working configuration.
</p>
<p>
  <strong>Backups:</strong>  Backups are simply backups of world data.  The
  same interface that is used for snapshots is used for backups as well.
</p>
<p>
  <strong>Multiple Interface Types:</strong>  Baskit has both an interactive
  shell and command-line options.  
<br />

<h3>Prerequisites</h3>
<p>
  Baskit is written in python and requires Python 2.6 or 2.7.  Most Debian or
  Ubuntu systems of a recent vintage (within the last 2-3yrs) will have Python
  2.6 or 2.7 installed by default and will not require any extra work.  For
  RHEL or CentOS hosts, the following is needed in order to install Python 2.6
</p>
<ol>
  <li><code>wget http://download.fedoraproject.org/pub/epel/5/i386/epel-release-5-4.noarch.rpm</code></li>
  <li><code>rpm -ivh epel-release-5-4.noarch.rpm</code></li>
  <li><code>yum -y install python26</code></li>
</ol>
<p>
  Baskit also relies on screen to background the bukkit server and java is
  needed in order to run bukkit.  Baskit will try to check to see if these
  exist and will prompt you if either of them does not exist.
</p>

<h3>Building a new bukkit server using baskit</h3>
<p>
  Currently Baskit is a Unix-only tool as it depends on screen to handle
  backgrounding the java process.  Work is being done to try to get baskit
  working for Windows as well, and there have been success stories getting it
  working on Windows via CygWin, however this walkthrough will focus on Linux
  installations.
</p>

<ol><p>Perform the following as a priviledged user:</p>
  <li>Make sure screen and a java JRE is installed.  If baskit complains
      about either of these packages missing, then you do not have them both
      installed.  Baskit will attempt to give you a command for your distro
      to install the needed files, however this is not guarenteed to work and
      it is up to you to make sure that both screen and java is installed.</li>
  <li>Download the script: <code>wget -O /usr/local/bin/baskit http://bukget.org/baskit/download</code></li>
  <li>Make sure it's executable: <code>chmod 755 /usr/local/bin/baskit</code></li>
  <ul>For CentOS Users
    <li><code>sed 's/\#\!\/usr\/bin\/env pynv python2.6/g' /usr/local/bin/baskit /tmp/baskit2</code></li>
    <li><code>mv /tmp/baskit2 /usr/local/bin/baskit</code></li>
  </ul>
  <li>Create the location for the minecraft server environment: <code>mkdir /opt/minecraft</code></li>
  <li>Goto your new empty environment: <code>cd /opt/minecraft</code></li>
  <li>Tell Baskit to download the latest stable Bukkit binary: <code>baskit update -s</code></li>
  <li>Tell Baskit to start the Bukkit server: <code>baskit start</code></li>
</ol>
<p>
  Thats it!  you should have a running system now using baskit.
</p>
<h3>Migrate an existing bukkit server to use baskit</h3>
<p>
  Currently Baskit is a Unix-only tool as it depends on screen to handle
  backgrounding the java process.  Work is being done to try to get baskit
  working for Windows as well, and there have been success stories getting it
  working on Windows via CygWin, however this walkthrough will focus on Linux
  installations.
</p>

<ol><p>Perform the following as a priviledged user:</p>
  <li>Download the script: <code>wget -O /usr/local/bin/baskit http://bukget.org/baskit/download</code></li>
  <li>Make sure it's executable: <code>chmod 755 /usr/local/bin/baskit</code></li>
  <ul>For CentOS Users
    <li><code>sed 's/\#\!\/usr\/bin\/env pynv python2.6/g' /usr/local/bin/baskit /tmp/baskit2</code></li>
    <li><code>mv /tmp/baskit2 /usr/local/bin/baskit</code></li>
  </ul>
  <li>Create the location for the minecraft server environment: <code>mkdir /opt/minecraft</code></li>
  <li>Goto your new empty environment: <code>cd /opt/minecraft</code></li>
  <li>Shutdown the existing bukkit server.</li>
  <li>Run Baskit to generate the config file and the environment: <code>baskit exit</code></li>
  <li>Copy your existing bukkit environment into /opt/minecraft/env.</li>
  <li>Rename your bukkit server binary to craftbukkit.jar.</li>
  <li>Edit the baskit.ini file and change build= to equal your bukkit build number.</li>
  <li>Tell Baskit to start the Bukkit server: <code>baskit start</code></li>
</ol>
<p>
  Now everything should start up using baskit.
</p>  

%rebase layout title='Baskit'