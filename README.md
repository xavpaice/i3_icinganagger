Wrapper for checking Icinga status in i3bar
===========================================

This is a simple extension to the wrapper at
http://code.stapelberg.de/git/i3status/plain/contrib/wrapper.py to enable
checking icinga status for warnings without having the page open all the time.
It puts a little text in i3bar, and sends annoying toaster messages.

Requirements
------------

* Icinga or Nagios
* the server needs mklivestatus
* I've included a little widget 'livestatus.py' that you can run on the nagios server


Usage
-----

First, configure ~/.i3status.conf
```
 general {
        output_format = "i3bar"
        colors = true
        interval = 15
 }
```

I set the interval to 15 to be kinder to icinga, our box is under enough load
as it is.

Next, configure the nagios/icinga credentials in ~/.nagios.yaml (edit to
make it a name you like, and add your host info there:

```yaml
 ---
 <icinga-server-name>:
   host: <icinga host>
   port: <port>
 <another-nagios-server>:
   host: <icinga host>
   port: <port>
```

Copy the script to ~/i3status/contrib/i3_livestatusclient.py

Edit your ~/.i3/config bar section:
```
 bar {
        status_command i3status | ~/i3status/contrib/i3_livestatusclient.py
 }
```
Now restart i3.


Alternative wrapper for Icinga-web
==================================

Use i3_icinganagger.py instead if you have the icinga-web package installed and the API running.

This one only supports a single Icinga server, the format of the yaml is:

```yaml
 ---
 host: <icinga host>
 port: <port>
```


Alternative wrapper for Nagios
==============================

Same thing as above, but this version uses Paramiko to grab the status.dat file
from a remote Nagios box, and parse it.  That way, we don't need the Icinga API.

Usage
-----

You'll need to have the python-pynag package installed. I've tested this on
Ubuntu Trusty only.

Ensure SSH key exchange is done, and your user has access to the status.dat file.

Add a file ~/.nagios-hosts.yaml
```yaml
 ---
 Server1:
   statfile: '/var/lib/icinga/status.dat'
   host: 'server1hostname'
   username: 'username'
 Server2:
   statfile: '/var/lib/icinga/status.dat'
   host: 'server2hostname'
   username: 'username'
```

Copy the script to ~/i3status/contrib/i3_nagstatus.py

Edit your ~/.i3/config bar section:
```
 bar {
     status_command i3status | ~/i3status/contrib/i3_nagstatus.py
 }
```

Now restart i3.
