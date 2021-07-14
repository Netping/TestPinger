#!/usr/bin/python3

from os import path
import json
from protocol import *

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
    confdata += '    },\n'
    confdata += '    {\n'
    confdata += '        "protocol": "SNMP",\n'
    confdata += '        "polls_cnt": "2",\n'
    confdata += '        "polls": [\n'
    confdata += '            {\n'
    confdata += '                "pollID": "snmp1",\n'
    confdata += '                "pollURL": "125.227.188.172:31161",\n'
    confdata += '                "OID": ".1.3.6.1.2.1.1.1.0"\n'
    confdata += '                "period": "2",\n'
    confdata += '            },\n'
    confdata += '            {\n'
    confdata += '                "pollID": "ping2",\n'
    confdata += '                "pollURL": "125.227.188.172:31161",\n'
    confdata += '                "OID": ".1.3.6.1.2.1.1.3.0"\n'
    confdata += '                "period": "5",\n'
    confdata += '            }\n'
    confdata += '       ]\n'
    confdata += '    },\n'
    confdata += ']'
    with open('config.json', 'w') as config:
        config.write(confdata)
        print('Сonfig file created (config.json)')
        print('You should edit the config file')

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
        pingthreads = []
        snmpthreads = []
        for protocol in confdata:
            if protocol['protocol'] == 'PING':
                for poll in protocol['polls']:
                    pingthread = PingThread(poll['pollID'], poll['pollURL'], poll['size'], poll['period'])
                    pingthread.start()
                    pingthreads.append(pingthread)
            elif protocol['protocol'] == 'SNMP':
                for poll in protocol['polls']:
                    snmpthread = SNMPThread(poll['pollID'], poll['pollURL'], poll['OID'], poll['period'])
                    snmpthread.start()
                    snmpthreads.append(snmpthread)
            else:
                pass
        for thread in pingthreads:
            thread.join()
        for thread in snmpthreads:
            thread.join()
    except KeyboardInterrupt:
        for thread in pingthreads:
            thread.stop()
        for thread in snmpthreads:
            thread.stop()
        print("\nwait...")

if __name__ == "__main__":
    main()
