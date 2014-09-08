
import sqlite3, cqStatus, cqUtils, time
import logging

def trydb(dbfile, func, *args):
    i = 0
    while True:
        i = i+1
        cd = None
        try:
            cd = cqDB(dbfile)
            fun = getattr(cd, func)
            ret = fun(*args)
            cd.close()
            cd = None
            return ret
        except sqlite3.OperationalError, e:
            logging.debug('Database operation failed: %s. (%dth trials)', e, i)
            if cd:
                cd.close()
                cd = None
            time.sleep(0.1)
            

class cqDB:
    
    def __init__(self, dbfile):
        self.conn   = sqlite3.connect(dbfile)
        self.cursor = self.conn.cursor()

    def execute(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()
        return self.cursor.lastrowid

    def execMany(self, sql):
        self.cursor.executescript(sql)

    def getJobs(self, condition = '', adst = ''):
        if condition:
            condition = ' WHERE %s ' % condition

        self.cursor.execute('SELECT rowid,* FROM jobs %s %s' % (condition, adst))
        return self.cursor.fetchall()

    def updateJob(self, idx, job):
        vals = []
        for key in job.keys():
            vals.append(" %s='%s' " % (key, job[key]))
        #print "UPDATE jobs SET %s WHERE rowid='%d'" % (','.join(vals), int(idx))
        self.execute("UPDATE jobs SET %s WHERE rowid='%d'" % (','.join(vals), int(idx)))

    def insertJob(self, job):
        djob = {
            'submitdate': cqUtils.ts2ftime(),
            'status': cqStatus.PENDING,
            'priority': 0
        }
        djob.update(job);
        
        return self.execute('''
            INSERT INTO jobs (name, cmd, submitdate, status, priority)
            VALUES ('%s', '%s', '%s', '%s', '%s')
        ''' % (djob['name'], djob['cmd'], djob['submitdate'], djob['status'], djob['priority']))

    def getPaused(self, wpid):
        self.cursor.execute("SELECT paused FROM worker WHERE pid = '%d'" % wpid)
        return self.cursor.fetchone()[0]

    def setPaused(self, wpid, paused):
        self.execute("UPDATE worker SET paused = '%d' WHERE pid='%d'" % (int(paused), wpid))

    def insertWorker(self, pid, paused=0, startdate=None):
        if startdate == None:
            startdate = cqUtils.ts2ftime()
        return self.execute('''
            INSERT INTO worker (pid, paused, startdate)
            VALUES ('%d', '%d', '%s')
        ''' % (pid, paused, startdate))

    def deleteWorker(self, wpid):
        self.execute("DELETE FROM worker WHERE pid = '%d'" % wpid)

    def getWorkers(self):
        self.cursor.execute('SELECT rowid,* FROM worker')
        return self.cursor.fetchall()
    
    def truncate(self):
        self.execute("DELETE FROM worker")
        self.execute("DELETE FROM jobs");
    
    def close(self):
        self.cursor.close()
        self.cursor=None
        self.conn.close()
        self.conn = None

	
