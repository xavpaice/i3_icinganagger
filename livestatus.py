#!/usr/bin/env python

# little socket thingy to listen on a port, and answer some basic queries
import json
import socket
import mk_livestatus
import sys
from thread import *

HOST = ''
PORT = 8888

#Function for handling connections. This will be used to create threads
def clientthread(conn):
    #infinite loop so that function do not terminate and thread do not end.
    s = mk_livestatus.Socket("/var/lib/icinga/rw/live")
    icingaprobs = s.services.columns(
        'acknowledged',
        'scheduled_downtime_depth',
        'host_name',
        'description',
        'state').filter( 'state > 0')
    #Receiving from client
    data = conn.recv(50)
    reply = icingaprobs.call()
    # we have a list of dicts, iterate over each and we need to count stuff
    warning = 0
    critical = 0
    unknown = 0
    for service in reply:
        if (
            service['scheduled_downtime_depth'] == '0' and
            service['acknowledged'] == '0'
        ):
            if service['state'] == '1':
                warning += 1

            if service['state'] == '2':
                critical += 1

            if service['state'] == '3':
                unknown += 1

    status = {'warning': warning, 'critical': critical, 'unknown': unknown}
    message = json.dumps(status)
    conn.sendall(message)
    conn.close()
    print 'Ended connection'

def main():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serversocket.bind((HOST, PORT))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    serversocket.listen(5)

    while 1:
        #accept connections from outside
        (conn, addr) = serversocket.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        start_new_thread(clientthread, (conn, ))

    serversocket.close()

if __name__ == '__main__':
    main()
