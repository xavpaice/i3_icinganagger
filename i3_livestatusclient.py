#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script is a simple wrapper which prefixes each i3status line with custom
# information. It is a python reimplementation of:
# http://code.stapelberg.de/git/i3status/tree/contrib/wrapper.pl
#
# To use it, ensure your ~/.i3status.conf contains this line:
#     output_format = "i3bar"
# in the 'general' section.
# Then, in your ~/.i3/config, use:
#     status_command i3status | ~/i3status/contrib/i3_icinganagger.py
# In the 'bar' section.
#
# © 2012 Valentin Haenel <valentin.haenel@gmx.de>
# Copyright (c) 2014 Catalyst.net Ltd
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import os
import json
import yaml
import socket
from gi.repository import Notify

class colors:
    green  = '#00FF00'
    yellow = '#FFFF00'
    red    = '#FF0000'

def notify(warnings, criticals):
    message = """\
            Icinga status changed to:
        Warnings: %s
        Criticals: %s
        """ % (warnings, criticals)
    nag = Notify.Notification.new('Icinga Status Change',
                                  message,
                                  'dialog-warning')
    Notify.Notification.show(nag)


def get_livestatus(host, port):
    print "livestatus called with %s : %s" % (host, port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'made socket'
    except socket.error:
        print 'Failed to create socket'
        sys.exit()

    try:
        remote_ip = socket.gethostbyname(host)
        print "got ip of %s" % remote_ip

    except socket.gaierror:
        #could not resolve
        print 'Hostname could not be resolved. Exiting'
        sys.exit()

    #Connect to remote server
    s.connect((remote_ip , port))
    print 'socket open'

    try :
        s.sendall('hitme')
    except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()

    reply = s.recv(16384)
    print 'got to the point of closing socket'
    s.close()
    return json.loads(reply)

def run_checks(warnings, criticals, **conf):
    changed = False
    current_status = {}
    current_status['critical'] = 0
    current_status['warning'] = 0
    for server in conf:
        print conf
        print server
        try:
            current_status[server] = get_livestatus(conf[server]['host'],
                                                    conf[server]['port'])
            current_status['critical'] += current_status[server]['critical']
            current_status['warning'] += current_status[server]['warning']
        except:
            current_status[server] = {'warning': 'Unknown',
                                      'critical': 'Unknown'}
    if current_status['critical'] != criticals:
        changed = True
    elif current_status['warning'] != warnings:
        changed = True

    if current_status['critical'] > 0:
        color  = colors.red
    elif current_status['warning'] > 0:
        color  = colors.yellow
    else:
        color = colors.green
    current_status['color'] = color
    current_status['changed'] = changed
    return current_status

def print_line(message):
    """ Non-buffered printing to stdout. """
    sys.stdout.write(message + '\n')
    sys.stdout.flush()

def read_line():
    """ Interrupted respecting reader for stdin. """
    # try reading a line, removing any extra whitespace
    try:
        line = sys.stdin.readline().strip()
        # i3status sends EOF, or an empty line
        if not line:
            sys.exit(3)
        return line
    # exit on ctrl-c
    except KeyboardInterrupt:
        sys.exit()


def process_results(current_result):
    text = 'Icinga '
    criticals = current_result['critical']
    warnings = current_result['warning']
    for key, value in current_result.iteritems():
        if key not in ('color', 'changed', 'critical', 'warning'):
            text = text + "| %s: W: %d C: %d " % (key,
                                                  value['warning'],
                                                  value['critical'])
    # send gtk notification if there's a change
    if current_result['changed']:
        notify(warnings, criticals)
    return text


if __name__ == '__main__':
    Notify.init('Nag')
    warnings = 0
    criticals = 0
    config = os.environ['HOME'] + '/.nagios.yaml'
    try:
        with open(config, 'r') as f:
            conf = yaml.load(f)
    except:
        print "cannot open ~/.nagios.yaml"
        sys.exit(1)

    # Skip the first line which contains the version header.
    print_line(read_line())

    # The second line contains the start of the infinite array.
    print_line(read_line())

    while True:
        line, prefix = read_line(), ''
        # ignore comma at start of lines
        if line.startswith(','):
            line, prefix = line[1:], ','

        j = json.loads(line)
        # insert information into the start of the json, but could be anywhere
        current_result = run_checks(warnings, criticals, **conf)
        # store the result for the next check
        criticals = current_result['critical']
        warnings = current_result['warning']
        # here we can say for server in conf: current_result[server]['warning'] etc
        # but we need to change the structure of the result to an array of server dicts
        text = process_results(current_result)
        # insert the new text into the json
        j.insert(0,
                 {'full_text' : '%s' % text,
                  'color': '%s' % current_result['color'],
                  'name' : 'icinga'})
        # and echo back new encoded json
        print_line(prefix+json.dumps(j))
