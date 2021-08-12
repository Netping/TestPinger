#!/usr/bin/python3

import threading
from datetime import datetime
import time
from pythonping import ping
from pysnmp.entity.rfc3413.oneliner import cmdgen
import requests
from testpinger import *

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

    def checkthread(self, pollURL, size, period):
        if pollURL == self.url and int(size) == self.size and float(period) == self.period:
            return True
        else:
            return False

    def run(self):
        num = 0
        while not self._stoped:
            num += 1
            logging.info(
                '%s START %s num=%s (url=%s, period=%s, size=%s)' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')[:-3],
                                                                     self.ID, num, self.url, self.period,
                                                                     self.size))
            try:
                response_list = ping(self.url, size=self.size, count=1)
                logging.info(
                    '%s  STOP %s num=%s (url=%s, period=%s, size=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')[:-3],
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
    def __init__(self, pollID, pollURL, OID, period, community, timeout):
        threading.Thread.__init__(self)
        self.ID = pollID
        self.url = pollURL.split(':')
        self.period = float(period)
        self.OID = OID
        self.community = community
        self.timeout = float(timeout)
        self._stoped = False

    def stop(self):
        self._stoped = True

    def checkthread(self, pollURL, OID, period, community, timeout):
        if pollURL == self.url and OID == self.OID and float(period) == self.period and \
                community == self.community and timeout == self.timeout:
            return True
        else:
            return False

    def run(self):
        num = 0
        while not self._stoped:
            num += 1
            logging.info(
                '%s START %s num=%s (url=%s, period=%s, OID=%s, timeout=%s)' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')[:-3],
                                                                     self.ID, num, self.url, self.period,
                                                                     self.OID, self.timeout))
            try:
                snmpget = cmdgen.CommandGenerator()
                errorIndication, errorStatus, errorIndex, varBinds = snmpget.getCmd(
                    cmdgen.CommunityData(self.community, mpModel=0),
                    cmdgen.UdpTransportTarget((self.url[0], int(self.url[1])), timeout=self.timeout, retries=0),
                    self.OID
                )
                if errorIndication:
                    # print("STOP {0} WITH ERROR: {1}".format(self.ID, errorIndication))
                    logging.info(
                        '%s  STOP %s num=%s (url=%s, period=%s, OID=%s, timeout=%s) result=%s' % (
                        datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                        self.ID, num, self.url, self.period,
                        self.OID, self.timeout, errorIndication))
                    # break
                elif errorStatus:
                    # print("STOP {0} with {1} at {2}".format(self.ID, errorStatus.prettyPrint(),
                    #                                         errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                    logging.info(
                        '%s  STOP %s num=%s (url=%s, period=%s, OID=%s, timeout=%s) result=%s' % (
                            datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                            self.ID, num, self.url, self.period,
                            self.OID, self.timeout, errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                    # break
                else:
                    result = ''
                    for varBind in varBinds:
                        result += str(varBind)
                    logging.info(
                        '%s  STOP %s num=%s (url=%s, period=%s, OID=%s, timeout=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')[:-3],
                                                                                                  self.ID, num, self.url,
                                                                                                  self.period, self.OID,
                                                                                                  self.timeout, result))
                time.sleep(self.period)
            except (OSError, RuntimeError) as e:
                print("STOP {0} WITH ERROR: {1}".format(self.ID, e))
                logging.error(
                    '%s  STOP %s num=%s (url=%s, period=%s, OID=%s, timeout=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                                                                              self.ID, num, self.url,
                                                                                              self.period, self.OID,
                                                                                              self.timeout, "ERROR: {0}".format(e)))
                break

class HttpThread(threading.Thread):
    def __init__(self, pollID, pollURL, period, timeout, authuser, authpwd):
        threading.Thread.__init__(self)
        self.ID = pollID
        self.url = pollURL
        self.period = float(period)
        self.timeout = float(timeout)
        self.authuser = authuser
        self.authpwd = authpwd
        self._stoped = False

    def stop(self):
        self._stoped = True

    def checkthread(self, pollURL, period, timeout, authuser, authpwd):
        if pollURL == self.url and float(period) == self.period and float(timeout) == self.timeout and authuser == self.authuser and authpwd == self.authpwd:
            return True
        else:
            return False

    def run(self):
        num = 0
        while not self._stoped:
            num += 1
            logging.info(
                '%s START %s num=%s (url=%s, period=%s, timeout=%s)' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')[:-3],
                                                                     self.ID, num, self.url, self.period,
                                                                     self.timeout))
            try:
                response = requests.get(self.url, auth=(self.authuser, self.authpwd), timeout=self.timeout)
                result = '(' + str(response.status_code) + ') ' + (response.text if response.status_code == 200 else 'empty')
                logging.info(
                    '%s  STOP %s num=%s (url=%s, period=%s, timeout=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')[:-3],
                                                                                   self.ID, num, self.url, self.period,
                                                                                   self.timeout, result))
                time.sleep(self.period)
            except requests.exceptions.ConnectTimeout:
                logging.info(
                    '%s  STOP %s num=%s (url=%s, period=%s, timeout=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                                                                   self.ID, num, self.url, self.period,
                                                                                   self.timeout, 'Connection timeout'))
                time.sleep(self.period)
            except requests.exceptions.ConnectionError:
                logging.info(
                    '%s  STOP %s num=%s (url=%s, period=%s, timeout=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                                                                   self.ID, num, self.url, self.period,
                                                                                   self.timeout, 'Host is unreachable'))
                time.sleep(self.period)
            except (OSError, RuntimeError) as e:
                print("STOP {0} WITH ERROR: {1}".format(self.ID, e))
                logging.error(
                    '%s  STOP %s num=%s (url=%s, period=%s, timeout=%s) result=%s' % (datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                                                                                   self.ID, num, self.url, self.period,
                                                                                   self.timeout, "ERROR: {0}".format(e)))
                break
