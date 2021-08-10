#!/usr/bin/python3
import time

import threading
import testpinger
import protocol
import ubus

# global variables
conf_files = {'ping': 'pingconf', 'snmp': 'snmpconf', 'http': 'httpconf'}
confdata = []
pingthreads = []
snmpthreads = []
httpthreads = []

class ReParseConfig(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def reparseconfig(self, event, data):
        global pingthreads
        global snmpthreads
        global httpthreads
        global confdata
        testpinger.parseconfig(data['config'], False)
        temppingthreads = []
        tempsnmpthreads = []
        temphttpthreads = []
        if data['config'][:4] == 'ping':
            # search changed and removed polls in pingconf
            for thread in pingthreads:
                thind = pingthreads.index(thread)
                thkey = list(thread.keys())[0]
                thval = list(thread.values())[0]
                th = next((item for item in confdata if item[".name"] == thkey), False)
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
                        pingthread = protocol.PingThread(th['.name'], th['pollURL'], th['size'], th['period'])
                        pingthread.start()
                        temppingthreads.append({th['.name']: pingthread})
            pingthreads += temppingthreads
            # search new polls
            for poll in confdata:
                notnewpoll = next((item for item in pingthreads if poll['.name'] in item.keys()), False)
                if not notnewpoll:
                    pingthread = protocol.PingThread(poll['.name'], poll['pollURL'], poll['size'],
                                                     poll['period'])
                    pingthread.start()
                    pingthreads.append({poll['.name']: pingthread})
        if data['config'][:4] == 'snmp':
            # search changed and removed polls in snmpconfig
            for thread in snmpthreads:
                thind = snmpthreads.index(thread)
                thkey = list(thread.keys())[0]
                thval = list(thread.values())[0]
                th = next((item for item in confdata if item[".name"] == thkey), False)
                if not th:
                    snmpthreads[thind][thkey].stop()
                    snmpthreads.pop(thind)
                else:
                    equal = thval.checkthread(th['pollURL'], th['OID'], th['period'], th['community'],
                                              th['timeout'])
                    if equal:
                        continue
                    else:
                        snmpthreads[thind][thkey].stop()
                        snmpthreads.pop(thind)
                        snmpthread = protocol.SNMPThread(th['.name'], th['pollURL'], th['OID'], th['period'],
                                                         th['community'], th['timeout'])
                        snmpthread.start()
                        tempsnmpthreads.append({th['.name']: snmpthread})
            snmpthreads += tempsnmpthreads
            # search new polls
            for poll in confdata:
                notnewpoll = next((item for item in snmpthreads if poll['.name'] in item.keys()), False)
                if not notnewpoll:
                    snmpthread = protocol.SNMPThread(poll['.name'], poll['pollURL'], poll['OID'],
                                                     poll['period'], poll['community'], poll['timeout'])
                    snmpthread.start()
                    snmpthreads.append({poll['.name']: snmpthread})
        if data['config'][:4] == 'snmp':
            # search changed and removed polls in snmpconfig
            for thread in httpthreads:
                thind = httpthreads.index(thread)
                thkey = list(thread.keys())[0]
                thval = list(thread.values())[0]
                th = next((item for item in confdata if item[".name"] == thkey), False)
                if not th:
                    httpthreads[thind][thkey].stop()
                    httpthreads.pop(thind)
                else:
                    equal = thval.checkthread(th['pollURL'], th['period'], th['timeout'])
                    if equal:
                        continue
                    else:
                        httpthreads[thind][thkey].stop()
                        httpthreads.pop(thind)
                        httpthread = protocol.HttpThread(th['.name'], th['pollURL'], th['period'], th['timeout'])
                        httpthread.start()
                        temphttpthreads.append({th['.name']: httpthread})
            httpthreads += temphttpthreads
            # search new polls
            for poll in confdata:
                notnewpoll = next((item for item in httpthreads if poll['.name'] in item.keys()), False)
                if not notnewpoll:
                    httpthread = protocol.HttpThread(poll['.name'], poll['pollURL'], poll['period'], poll['timeout'])
                    httpthread.start()
                    httpthreads.append({poll['.name']: httpthread})

    def run(self):
        # ubus.connect()
        ubus.listen(("commit", self.reparseconfig))
        ubus.loop()

