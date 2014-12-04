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


# quick checker for nagios status

import json
import os
import sys

from pynag.Parsers import status
import paramiko
import yaml


class colors:
    green = '#00FF00'
    yellow = '#FFFF00'
    red = '#FF0000'


def print_line(message):
    sys.stdout.write(message + '\n')
    sys.stdout.flush()


def read_line():
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


def get_statusfiles(services):
    # ssh to each server in the config, grab the status.dat and put it in
    # the location specified in the config
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for region in services.keys():
        services[region]['pulled_statfile'] = '/tmp/' + region + 'status.dat'
        ssh.connect(services[region]['host'],
                    username=services[region]['username'])
        ftp = ssh.open_sftp()
        ftp.get(services[region]['statfile'],
                services[region]['pulled_statfile'])
        ftp.close()
        ssh.close()


def parse_status(services):
    # parse the status.dat files listed in the config
    # return the status of the servers in a hash
    for region in services.keys():
        services[region]['warning'] = 0
        services[region]['critical'] = 0
        services[region]['unknown'] = 0
        services[region]['color'] = colors.green
        s = status(services[region]['pulled_statfile'])
        s.parse()
        for service in s.data.get('servicestatus', []):
            if (int(service.get('scheduled_downtime_depth', None)) == 0
                    and int(service.get('problem_has_been_acknowledged',
                                        None)) == 0):
                # get all the 'not OK' services
                if (int(service.get('current_state', None)) == 1):
                    services[region]['warning'] += 1
                elif (int(service.get('current_state', None)) == 2):
                    services[region]['critical'] += 1
                elif (int(service.get('current_state', None)) == 3):
                    services[region]['unknown'] += 1

            if services[region]['critical'] > 0:
                services[region]['color'] = colors.red
            elif services[region]['warning'] > 0:
                services[region]['color'] = colors.yellow

    return services


if __name__ == '__main__':
    config = os.environ['HOME'] + '/.nagios-hosts.yaml'
    try:
        with open(config, 'r') as f:
            nagios_hosts = yaml.load(f)
    except:
        print "cannot open ~/.nagios-hosts.yaml"
        sys.exit(1)

    # Skip the first line which contains the version header.
    print_line(read_line())

    # The second line contains the start of the infinite array.
    print_line(read_line())

    while True:
        line, prefix = read_line(), ''
        if line.startswith(','):
            line, prefix = line[1:], ','

        j = json.loads(line)

        get_statusfiles(nagios_hosts)
        servicestatus = parse_status(nagios_hosts)
        # put the output into the json
        for region in servicestatus.keys():
            text = "{}: Warn: {} Crit: {}".format(
                region,
                servicestatus[region]['warning'],
                servicestatus[region]['critical'])
            j.insert(0, {'full_text': '%s' % text, 'color': '%s' %
                         servicestatus[region]['color'], 'name': region})

        output_line = prefix + json.dumps(j)
        print_line(output_line)
