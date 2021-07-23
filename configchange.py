#!/usr/bin/python3
import time

import pyinotify
import threading
import testpinger
import protocol

# global variables
conf_files = {'ping': 'pingconf', 'snmp': 'snmpconf'}
confdata = []
confchange = False
pingthreads = []
snmpthreads = []

class ConfigChange(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        global confchange
        # print("MODIFY event:", event.pathname.split('/')[-1:][0])
        confchange = event.pathname.split('/')[-1:][0]

class ReParseConfig(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stoped = False

    def stop(self):
        self._stoped = True

    def run(self):
        global pingthreads
        global snmpthreads
        global confdata
        global confchange
        while not self._stoped:
            if confchange:
                temppingthreads = []
                tempsnmpthreads = []
                testpinger.parseconfig(confchange, False)
                if confchange[:4] == 'ping':
                    # search changed and removed polls in pingconf
                    for thread in pingthreads:
                        thind = pingthreads.index(thread)
                        thkey = list(thread.keys())[0]
                        thval = list(thread.values())[0]
                        th = next((item for item in confdata if item["pollID"] == thkey), False)
                        if not th:
                            pingthreads[thind][thkey].stop()
                            pingthreads.pop(thind)
                        else:
                            equal = thval.checkthread(th['pollURL'], th['size'], th['period'])
                            if equal:
                                continue
                            else:
                                pingthreads[thind][thkey].stop()
                                pingthreads.pop(thind)
                                pingthread = protocol.PingThread(th['pollID'], th['pollURL'], th['size'], th['period'])
                                pingthread.start()
                                temppingthreads.append({th['pollID']: pingthread})
                    pingthreads += temppingthreads
                    # search new polls
                    for poll in confdata:
                        notnewpoll = next((item for item in pingthreads if poll['pollID'] in item.keys()), False)
                        if not notnewpoll:
                            pingthread = protocol.PingThread(poll['pollID'], poll['pollURL'], poll['size'],
                                                             poll['period'])
                            pingthread.start()
                            pingthreads.append({poll['pollID']: pingthread})
                if confchange[:4] == 'snmp':
                    # search changed and removed polls in snmpconfig
                    for thread in snmpthreads:
                        thind = snmpthreads.index(thread)
                        thkey = list(thread.keys())[0]
                        thval = list(thread.values())[0]
                        th = next((item for item in confdata if item["pollID"] == thkey), False)
                        if not th:
                            snmpthreads[thind][thkey].stop()
                            snmpthreads.pop(thind)
                        else:
                            equal = thval.checkthread(th['pollURL'], th['OID'], th['period'], th['community'])
                            if equal:
                                continue
                            else:
                                snmpthreads[thind][thkey].stop()
                                snmpthreads.pop(thind)
                                snmpthread = protocol.SNMPThread(th['pollID'], th['pollURL'], th['OID'], th['period'],
                                                                 th['community'])
                                snmpthread.start()
                                tempsnmpthreads.append({th['pollID']: snmpthread})
                    snmpthreads += tempsnmpthreads
                    # search new polls
                    for poll in confdata:
                        notnewpoll = next((item for item in snmpthreads if poll['pollID'] in item.keys()), False)
                        if not notnewpoll:
                            snmpthread = protocol.SNMPThread(poll['pollID'], poll['pollURL'], poll['OID'],
                                                             poll['period'], poll['community'])
                            snmpthread.start()
                            snmpthreads.append({poll['pollID']: snmpthread})
                confchange = False
                # for thread in temppingthreads:
                #     for th in thread.values():
                #         th.join()
                # for thread in tempsnmpthreads:
                #     for th in thread.values():
                #         th.join()
            time.sleep(5)


