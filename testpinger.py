#!/usr/bin/python3

import logging
from os import path
from protocol import *
from configchange import *
import sys

# parse config file
def parseconfig(file, start):
    if not start:
        confdata.clear()
    try:
        ubus.connect()
    except:
        pass
    confvalues = ubus.call("uci", "get", {"config": file})
    poll_ids = []
    for confdict in list(confvalues[0]['values'].values()):
        if confdict['.name'] not in poll_ids:
            confdict['protocol'] = file[:4]
            confdata.append(confdict)
            poll_ids.append(confdict['.name'])
    # ubus.disconnect()


def main():
    try:
        print('TESTPINGER 5.2')
        print('PRESS "CTRL + C" TO QUIT')
        # create and initialize log file
        logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(message)s')

        # read existing config files
        global confdata
        confdata = []
        for file in conf_files.values():
            if path.exists(file):
                parseconfig(file, True)
        # polling
        global pingthreads
        global snmpthreads
        global httpthreads
        for poll in confdata:
            if poll['protocol'] == 'ping':
                pingthread = PingThread(poll['.name'], poll['pollURL'], poll['size'], poll['period'])
                pingthread.start()
                pingthreads.append({poll['.name']: pingthread})
            elif poll['protocol'] == 'snmp':
                snmpthread = SNMPThread(poll['.name'], poll['pollURL'], poll['OID'],
                                        poll['period'], poll['community'], poll['timeout'])
                snmpthread.start()
                snmpthreads.append({poll['.name']: snmpthread})
            elif poll['protocol'] == 'http':
                httpthread = HttpThread(poll['.name'], poll['pollURL'], poll['period'], poll['timeout'], poll['authuser'], poll['authpwd'])
                httpthread.start()
                httpthreads.append({poll['.name']: httpthread})
            else:
                pass
        reparseconfig = ReParseConfig()
        reparseconfig.daemon = True
        reparseconfig.start()
        # for thread in pingthreads:
        #     for th in thread.values():
        #         th.join()
        # for thread in snmpthreads:
        #     for th in thread.values():
        #         thread.join()
        #reparseconfig.join()
    except KeyboardInterrupt:
        print("\nwait...")
        for thread in pingthreads:
            for th in thread.values():
                th.stop()
        for thread in snmpthreads:
            for th in thread.values():
                th.stop()
        for thread in httpthreads:
            for th in thread.values():
                th.stop()


if __name__ == "__main__":
    main()
