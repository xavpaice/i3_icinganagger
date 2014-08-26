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
import pynotify
import yaml
import requests

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
    notification = pynotify.Notification("Icinga status change", 
                    message, "dialog-warning")
    notification.show()

def check_icinga(status, auth_key, host, proto, port, proxies):
    url = ("{proto}://{host}:{port}/icinga-web/web/api/service/filter%5B" +
          "AND(SERVICE_CURRENT_PROBLEM_STATE%7C=%7C{status};" +
          "SERVICE_CURRENT_PROBLEM_STATE%7C=%7C{status})%5D/columns%5B" +
          "SERVICE_NAME%7CSERVICE_CURRENT_PROBLEM_STATE%5D/countColumn=" +
          "SERVICE_ID/authkey={auth_key}/json").format(**vars())
    result = requests.get(url, proxies=proxies, verify=False)
    return json.loads(result.text)

def run_checks(warnings, criticals, **conf):
    changed = False
    current_warnings = check_icinga(1, conf['auth_key'], 
                                    conf['host'], conf['proto'],
                                    conf['port'], conf['proxies'])
    current_criticals = check_icinga(2, conf['auth_key'], 
                                     conf['host'], conf['proto'],
                                     conf['port'], conf['proxies'])

    if current_criticals['total'] != criticals:
        changed = True
    elif current_warnings['total'] != warnings:
        changed = True
    
    if current_criticals['total'] > 0:
        color  = colors.red
    elif current_warnings['total'] > 0:
        color  = colors.yellow
    else:
        color = colors.green
    
    return { 'warnings': current_warnings['total'], 
             'criticals': current_criticals['total'], 
             'color': color, 
             'changed': changed
             }

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

if __name__ == '__main__':
    pynotify.init("Icinga")
    warnings = 0
    criticals = 0
    config = os.environ['HOME'] + '/.nagios-creds.yaml'
    try:
        with open(config, 'r') as f:
            conf = yaml.load(f)
    except:
        print "cannot open ~/.nagios-creds.yaml"
        sys.exit(1)

    if not 'proxies' in conf:
        conf['proxies'] = ''
    
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
        criticals = current_result['criticals']
        warnings = current_result['warnings']
        text = "Warnings: %s   Criticals: %s" % (warnings, criticals)
        
        # send gtk notification if there's a change
        if current_result['changed']:
            notify(warnings, criticals)
        
        # insert the new text into the json
        j.insert(0, {'full_text' : '%s' % text, 'color': '%s' %
                     current_result['color'], 'name' : 'icinga'})
        # and echo back new encoded json
        print_line(prefix+json.dumps(j))






