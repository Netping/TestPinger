#!/usr/bin/python3

import threading
import logging
from datetime import datetime
import time
from pythonping import ping
from pysnmp.entity.rfc3413.oneliner import cmdgen

class PingThread(threading.Thread):
    def __init__(self, pollID, pollURL, size, period):
        threading.Thread.__init__(self)
        self.ID = pollID
        self.url = pollURL
        self.period = float(period)
        self.size = int(size)
        self._stoped = False

    def stop(self):
        self._stoped = True

    def run(self):
        num = 0
        while not self._stoped:
            num += 1
            logging.info(
                '%s START %s num=%s (url=%s, period=%s, size=%s)' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                                                     self.ID, num, self.url, self.period,
                                                                     self.size))
            try:
                response_list = ping(self.url, size=self.size, count=1)
                logging.info(
                    '%s  STOP %s num=%s (url=%s, period=%s, size=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                                                                   self.ID, num, self.url, self.period,
                                                                                   self.size, response_list._responses))
                time.sleep(self.period)
            except (OSError, RuntimeError) as e:
                print("STOP {0} WITH ERROR: {1}".format(self.ID, e))
                logging.error(
                    '%s  STOP %s num=%s (url=%s, period=%s, size=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                                                                   self.ID, num, self.url, self.period,
                                                                                   self.size, "ERROR: {0}".format(e)))
                break

class SNMPThread(threading.Thread):
    def __init__(self, pollID, pollURL, OID, period):
        threading.Thread.__init__(self)
        self.ID = pollID
        self.url = pollURL.split(':')
        self.period = float(period)
        self.OID = OID
        self._stoped = False

    def stop(self):
        self._stoped = True

    def run(self):
        num = 0
        while not self._stoped:
            num += 1
            logging.info(
                '%s START %s num=%s (url=%s, period=%s, OID=%s)' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                                                     self.ID, num, self.url, self.period,
                                                                     self.OID))
            try:
                snmpget = cmdgen.CommandGenerator()
                errorIndication, errorStatus, errorIndex, varBinds = snmpget.getCmd(
                    cmdgen.CommunityData('public', mpModel=0),
                    cmdgen.UdpTransportTarget((self.url[0], self.url[1])),
                    self.OID
                )
                if errorIndication:
                    print("STOP {0} WITH ERROR: {1}".format(self.ID, errorIndication))
                    logging.error(
                        '%s  STOP %s num=%s (url=%s, period=%s, OID=%s) result=%s' % (
                        datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                        self.ID, num, self.url, self.period,
                        self.OID, "ERROR: {0}".format(errorIndication)))
                    break
                elif errorStatus:
                    print("STOP {0} with {1} at {2}".format(self.ID, errorStatus.prettyPrint(),
                                                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                    logging.error(
                        '%s  STOP %s num=%s (url=%s, period=%s, OID=%s) result=%s' % (
                            datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                            self.ID, num, self.url, self.period,
                            self.OID, errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                    break
                else:
                    result = ''
                    for varBind in varBinds:
                        result.join([x.prettyPrint() for x in varBind])
                    logging.info(
                        '%s  STOP %s num=%s (url=%s, period=%s, OID=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                                                                      self.ID, num, self.url, self.period,
                                                                                      self.OID, result))
                time.sleep(self.period)
            except (OSError, RuntimeError) as e:
                print("STOP {0} WITH ERROR: {1}".format(self.ID, e))
                logging.error(
                    '%s  STOP %s num=%s (url=%s, period=%s, OID=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                                                                   self.ID, num, self.url, self.period,
                                                                                   self.OID, "ERROR: {0}".format(e)))
                break