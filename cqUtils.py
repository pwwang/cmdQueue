
import sqlite3, os, time
from datetime import datetime
from subprocess import check_output

def ftime2ts(ftime='now'): #'%Y-%m-%d %H:%M:%S' to timestamp
    if ftime == 'now':
        ftime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    ptime = time.strptime(ftime, '%Y-%m-%d %H:%M:%S')
    return int(time.mktime(ptime))

def ts2ftime(ts=0): #timestamp to '%Y-%m-%d %H:%M:%S'
    if ts == 0:
        ts = ftime2ts()
    return time.strftime('%Y-%m-%d %H:%M:%S', datetime.fromtimestamp(ts).timetuple())

def checkWorker(wpid):
    if os.name == 'nt':
        cmdline = check_output('WMIC PROCESS where ProcessId=%d get CommandLine /FORMAT:LIST' % wpid)
        return 'cqWorker' in cmdline
    else:
        clfile = '/proc/%s/cmdline' % wpid
        if not os.path.isfile(clfile):
            return False
        f = open(clfile)
        cmdline = f.read()
        f.close()
        return 'cqWorker' in cmdline


