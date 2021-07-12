#!/usr/bin/python3

from os import path
import json
import threading
import logging
from datetime import datetime
import time
from pythonping import ping

def create_conf_example():
    confdata = '[\n'
    confdata += '    {\n'
    confdata += '        "protocol": "PING",\n'
    confdata += '        "polls_cnt": "2",\n'
    confdata += '        "polls": [\n'
    confdata += '            {\n'
    confdata += '                "pollID": "ping1",\n'
    confdata += '                "pollURL": "localhost",\n'
    confdata += '                "period": "0.5",\n'
    confdata += '                "size": "10"\n'
    confdata += '            },\n'
    confdata += '            {\n'
    confdata += '                "pollID": "ping2",\n'
    confdata += '                "pollURL": "localhost",\n'
    confdata += '                "period": "5",\n'
    confdata += '                "size": "10"\n'
    confdata += '            }\n'
    confdata += '       ]\n'
    confdata += '   }\n'
    confdata += ']'
    with open('config.json', 'w') as config:
        config.write(confdata)
        print('Сonfig file created (config.json)')
        print('You should edit the config file')

class PingThread(threading.Thread):
    def __init__(self, pollID, pollURL, period, size):
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

def main():
    try:
        # create config file if it doesn’t exist
        if not path.exists('./config.json'):
            create_conf_example()
            return
        print('PRESS "CTRL + C" TO QUIT')
        # create and initialize log file
        logging.basicConfig(filename='log.txt', level=logging.INFO)
        # read existing config file
        with open('./config.json') as config:
            confdata = json.load(config)
        # polling
        for protocol in confdata:
            threads = []
            for poll in protocol['polls']:
                pingthread = PingThread(poll['pollID'], poll['pollURL'], poll['period'], poll['size'])
                pingthread.start()
                threads.append(pingthread)
            for thread in threads:
                thread.join()
    except KeyboardInterrupt:
        for thread in threads:
            thread.stop()
        print("\nwait...")

if __name__ == "__main__":
    main()
