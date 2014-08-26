Wrapper for checking Icinga status in i3bar
===========================================

This is a simple extension to the wrapper at
http://code.stapelberg.de/git/i3status/plain/contrib/wrapper.py to enable
checking icinga status for warnings without having the page open all the time.
It puts a little text in i3bar, and sends annoying toaster messages.

Usage
-----

First, configure ~/.i3status.conf
 general {
        output_format = "i3bar"
        colors = true
        interval = 15
 }

I set the interval to 15 to be kinder to icinga, our box is under enough load
as it is.

Next, configure the nagios/icinga credentials in ~/.nagios-creds.yaml (edit to
make it a name you like, and add your host info there:

 ---
 host: <icinga host>
 port: <port>
 proto: <http or https>
 auth_key: <your auth key>
 proxy: <optional>

Copy the script to ~/i3status/contrib/i3_icinganagger.py

Edit your ~/.i3/config bar section:

 bar {
        status_command i3status | ~/i3status/contrib/i3_icinganagger.py
 }

Now restart i3.
