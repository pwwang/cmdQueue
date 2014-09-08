
from multiprocessing import Process
from subprocess import Popen
from cqDB import trydb
from tempfile import gettempdir
import cqStatus, cqUtils, shlex, time, os, sys, logging, json, md5
from cqPlugin import cqPlugin

def setLock(lf=None):
    if lf == None:
        lf = lockFile # global var cannot be passed into Process
    logging.debug('Set lock ...')
    open(lf, 'w').close()

def getLock(lf=None):
    if lf == None:
        lf = lockFile # global var cannot be passed into Process
    logging.debug('Get lock: %d', os.path.isfile('lock'))
    return os.path.isfile(lf)

def releaseLock(lf=None):
    if lf == None:
        lf = lockFile # global var cannot be passed into Process
    logging.debug('Release lock ...')
    if os.path.isfile(lf):
        os.remove(lf)
    

class cmdWorker:

    def __init__(self, dbfile, interval):
        self.dbfile = dbfile
        self.interval = interval
        
    def getRunnableJob(self):
        logging.debug('Try to get runnable job ...')
        job = trydb(self.dbfile, 'getJobs', "status='%s'" % cqStatus.PENDING, "ORDER BY priority, submitdate LIMIT 1")

        if len(job) > 0:
            logging.debug('Runnable job found: %s(%d)', job[0][1], job[0][0])
            return cmdJob(job[0][0], job[0][2], self.dbfile, lockFile)
        else:
            logging.debug('No runnable job found.')
            return False

    def getPaused(self):
        pid = os.getpid()
        logging.debug('Try to get pause status ...')
        paused = trydb(self.dbfile, 'getPaused', pid)
        return int(paused)

    def start(self):
        i = 0
        while True:
            i = i + 1
            if self.getPaused():
                logging.info('Worker paused, wait until it resumes.')
                time.sleep(self.interval)
            else:
                if not getLock():
                    setLock()
                    job = self.getRunnableJob()
                else:
                    job = None
                
                if job:
                    logging.info('Start to run job(%d)', job.jobid)
                    plugin.onJobStart(job.jobid, job.cmd)
                    job.start()
                    job.join()
                    logging.info('Job(%d) ended.', job.jobid)
                    plugin.onJobEnd(job.jobid, job.cmd)
                else:
                    if i%100 == 0:
                        logging.info('No pending jobs, wait.')
                    logging.debug('Not a valid job, wait until valid job added.')
                    time.sleep(self.interval)

class cmdJob (Process):

    def __init__(self, jobid, cmd, dbfile, lockfile):
        super(cmdJob, self).__init__()
        self.jobid = jobid
        self.cmd   = cmd
        self.dbfile = dbfile
        self.lockfile = lockfile

    def update(self, vals):
        logging.debug('[JOB: %d] Try to update job: %s', self.jobid, json.dumps(vals))
        trydb(self.dbfile, 'updateJob', self.jobid, vals)
    
    def run(self):
        logging.debug('[JOB: %d] Set startdate and status as %s', self.jobid, cqStatus.RUNNING)
        self.update({'status': cqStatus.RUNNING, 'startdate': cqUtils.ts2ftime()})
        releaseLock(self.lockfile)
        #self.plugin.onJobStart(self.jobid, self.cmd) # not supported on Windows
        args = shlex.split(self.cmd)
        
        try:
            logging.debug('[JOB: %d] Try to run job: %s', self.jobid, self.cmd)
            job = Popen(args)

            logging.debug('[JOB: %d] Try to save PID(%d) into database', self.jobid, job.pid)
            self.update({'pid': job.pid})
            logging.debug('[JOB: %d] Wait for job to finish', self.jobid)
            job.wait()
            if job.returncode == 0:
                logging.debug('[JOB: %d] Job finished normally, try to update the status and finishdate', self.jobid)
                self.update({'status': cqStatus.COMPLETE, 'finishdate': cqUtils.ts2ftime()})
            else:
                logging.debug('[JOB: %d] Job ended unexpectedly, try to update the status and finishdate', self.jobid)
                self.update({'status': cqStatus.KILLED, 'finishdate': cqUtils.ts2ftime()})
            #self.plugin.onJobEnd(self.jobid, self.cmd, job.returncode)
        except OSError, e:
            logging.debug('[JOB: %d] Job failed to start, try to update the status and finishdate', self.jobid)
            #self.plugin.onJobEnd(self.jobid, self.cmd, -99)
            self.update({'status': cqStatus.ERROR, 'finishdate': cqUtils.ts2ftime()})

        

if __name__ == '__main__' :
    pid      = os.getpid()
    dbfile   = sys.argv[1]
    interval = int(sys.argv[2])
    logfile  = sys.argv[3]
    loglevel = sys.argv[4]
    logging.basicConfig(filename=logfile, level=loglevel,format='[%(asctime)s][WORKER: '+ str(pid).ljust(5) +'][%(levelname)8s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.debug('Try to insert worker into database: %d' % pid)
    trydb(dbfile, 'insertWorker', pid)
    logging.info('Worker started at PID: %s', pid)
    
    lockFile = os.path.join(gettempdir(), 'cmdQueue-%s.lock' % md5.md5(dbfile).hexdigest())
    plugin = cqPlugin()
    plugin.onWorkerStart(pid)
    cmdWorker(dbfile, interval).start()
