#!/usr/bin/python3

import logging
from os import path
from protocol import *
from configchange import *

# parse config file
def parseconfig(file, start):
    if not start:
        confdata.clear()
    conf = open(file, 'r')
    strconf = conf.read()
    configs = strconf.split('config ')
    poll_ids = []
    for config in configs[1:]:
        parse_error = False
        confdict = {}
        poll = config.split('\n')
        confdict['protocol'] = file[:4]
        if poll[0] not in poll_ids:
            confdict['pollID'] = poll[0]
            for option in poll[1:]:
                opt = option.strip().split(' ')
                if len(opt) == 3:
                    confdict[opt[1]] = opt[2]
                elif len(opt) == 1 and opt[0] == '':
                    continue
                else:
                    print("CONFIG ERROR {0}: check config file in {1} with row: {2}".format(file, poll[0], option))
                    parse_error = True
        if not parse_error:
            poll_ids.append(poll[0])
            confdata.append(confdict)
    conf.close()

def main():
    try:
        # run config notifier
        wm = pyinotify.WatchManager()
        eh = ConfigChange()
        notifier = pyinotify.ThreadedNotifier(wm, eh)
        for file in conf_files.values():
            wm.add_watch(file, pyinotify.IN_MODIFY)
        notifier.start()
        print('TestPinger (version 0.3)')
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
        for poll in confdata:
            if poll['protocol'] == 'ping':
                pingthread = PingThread(poll['pollID'], poll['pollURL'], poll['size'], poll['period'])
                pingthread.start()
                pingthreads.append({poll['pollID']: pingthread})
            elif poll['protocol'] == 'snmp':
                snmpthread = SNMPThread(poll['pollID'], poll['pollURL'], poll['OID'],
                                        poll['period'], poll['community'])
                snmpthread.start()
                snmpthreads.append({poll['pollID']: snmpthread})
            else:
                pass
        reparseconfig = ReParseConfig()
        reparseconfig.start()
        # for thread in pingthreads:
        #     for th in thread.values():
        #         th.join()
        # for thread in snmpthreads:
        #     for th in thread.values():
        #         thread.join()
        # reparseconfig.join()
        notifier.join()
    except KeyboardInterrupt:
        print("\nwait...")
        for thread in pingthreads:
            for th in thread.values():
                th.stop()
        for thread in snmpthreads:
            for th in thread.values():
                th.stop()
        reparseconfig.stop()
        notifier.stop()


if __name__ == "__main__":
    main()
