Wrapper for checking Icinga status in i3bar
===========================================

This is a simple extension to the wrapper at
http://code.stapelberg.de/git/i3status/plain/contrib/wrapper.py to enable
checking icinga status for warnings without having the page open all the time.
It puts a little text in i3bar, and sends annoying toaster messages.

A simple console only version (i.e. just the text) is included (txtnagger.py)
so if you want, you can get similar info via ssh without any graphics.

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

Next, configure the nagios/icinga credentials in ~/.nagios-creds.yaml (edit to
make it a name you like, and add your host info there:

```yaml
 ---
 host: <icinga host>
 port: <port>
 proto: <http or https>
 auth_key: <your auth key>
 proxy: <optional>
```

Copy the script to ~/i3status/contrib/i3_icinganagger.py

Edit your ~/.i3/config bar section:
```
 bar {
        status_command i3status | ~/i3status/contrib/i3_icinganagger.py
 }
```
Now restart i3.


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
