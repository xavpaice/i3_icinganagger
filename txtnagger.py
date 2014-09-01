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
#     status_command i3status | ~/i3status/contrib/wrapper.py
# In the 'bar' section.
#
# In its current version it will display the cpu frequency governor, but you
# are free to change it to display whatever you like, see the comment in the
# source code below.
#
# © 2012 Valentin Haenel <valentin.haenel@gmx.de>
#
# This program is free software. It comes without any warranty, to the extent
# permitted by applicable law. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License (WTFPL), Version
# 2, as published by Sam Hocevar. See http://sam.zoy.org/wtfpl/COPYING for more
# details.

import sys
import os
import json
import yaml
import requests
import time

class colors:
    green  = '\033[92m'
    yellow = '\033[93m'
    red    = '\033[91m'
    endc   = '\033[0m'

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

if __name__ == '__main__':
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
    
    while True:
        # insert information into the start of the json, but could be anywhere
        current_result = run_checks(warnings, criticals, **conf)
        criticals = current_result['criticals']
        warnings = current_result['warnings']
        text = "%sWarnings: %s   Criticals: %s%s" % (current_result['color'], 
                                                     warnings, 
                                                     criticals,
                                                     colors.endc)
        print text
        time.sleep(15)






