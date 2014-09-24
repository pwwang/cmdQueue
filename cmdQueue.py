
import sqlite3, time, os, signal, argparse, cqUtils, cqStatus, ConfigParser, sys, md5
from multiprocessing import Process
from urlparse import parse_qs
from cqDB import cqDB
from cqPlugin import cqPlugin
from subprocess import Popen
from tempfile import gettempdir


class cmdQueue:

    def __init__(self, args):
        self.args = args
        self.db   = cqDB(args.db)

        
    def setup(self):
        self.db.execMany('''
            CREATE TABLE  IF NOT EXISTS jobs (
		name TEXT,
		cmd TEXT,
		pid INTEGER,
		submitdate TEXT,
		startdate TEXT,
		finishdate TEXT,
                status TEXT,
		priority INTEGER
            );
        
            CREATE TABLE  IF NOT EXISTS worker (
                    pid INTEGER,
                    paused INTEGER,
                    startdate TEXT
            );
	''');

        plugin.onSetup()

        print '! jobQueue has been set up.'

    def add(self, job):
        idx = self.db.insertJob(job)
        plugin.onJobSubmit(idx, job['name'], job['cmd'])
        print '! Job added: %s(%d).' % (job['name'], idx)

    def killJobByPID(self, pid):
        jobs = self.db.getJobs("pid='%d' AND status='%s'" % (pid, cqStatus.RUNNING))
        if len(jobs) > 0:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError, e:
                pass
            self.db.updateJob(jobs[0][0], {'status': cqStatus.KILLED, 'finishdate': cqUtils.ts2ftime()})
            plugin.onJobKill(jobs[0][0], pid, jobs[0][1], jobs[0][2])
            print '! Job %s(%d) was killed at PID: %d.' % (jobs[0][1], jobs[0][0], pid)
        else:
            print '! No running job at PID: %d, nothing to kill.' % pid
    
    def killJobByID(self, jid):
        jobs = self.db.getJobs("rowid=%d AND status='%s'" % (jid, cqStatus.RUNNING))
        if len(jobs) > 0:
            try:
                os.kill(jobs[0][3], signal.SIGTERM)
            except OSError, e:
                pass 
            self.db.updateJob(jid, {'status': cqStatus.KILLED, 'finishdate': cqUtils.ts2ftime()})
            plugin.onJobKill(jid, jobs[0][3], jobs[0][1], jobs[0][2])
            print '! Job %d was killed at PID: %d' % (jid, jobs[0][3])
        else:
            print '! Job %d is not running, nothing to kill.' % jid

    def killWorker(self, wpid):
        if wpid==0:
            workers = self.db.getWorkers()
            for worker in workers:
                self.killWorker(worker[1])
        else:
            try:
                os.kill (wpid, signal.SIGTERM)
            except OSError, e:
                pass
            self.db.deleteWorker(wpid)
            plugin.onWorkerKill(wpid)
            print '! Worker [%d] killed.' % wpid

    def pause(self, wpid):
        if wpid == 0:
            workers = self.db.getWorkers()
            for worker in workers:
                self.pause(worker[1])
        else:
            self.db.setPaused(wpid, 1)
            plugin.onWorkerPause(wpid)
            print '! Worker [%d] paused, no new jobs will be running (running jobs not killed).' % wpid

    def resume(self, wpid):
        if wpid == 0:
            workers = self.db.getWorkers()
            for worker in workers:
                self.resume(worker[1])
        else:
            self.db.setPaused(wpid, 0)
            plugin.onWorkerResume(wpid)
            print '! Worker [%d] resumed.' % wpid

    def start(self):
        workers = self.db.getWorkers()
        ret = self.args.workercount - len(workers)
        if ret <= 0:
            print '! Workers are running:'
            self.listWorkers()
        else:
            plugin.onQueueStart(args)
            print '! Starting workers ...'
            # workers will start at the end of the script
        return ret

    def stop(self):
        self.pause(0)
        jobs = self.db.getJobs("status='%s'" % cqStatus.RUNNING)
        for job in jobs:
            if job[3] == None:
                self.db.execute("DELETE FROM jobs WHERE rowid = '%s'" % job[0])
                print '! No PID for job %s(%d), delete it from database.' % (job[1], job[0])
            else:
                print '! Killing running job %d at PID: %d.' % (job[0], job[3])
                self.killJobByID(job[0])

        # kill workers
        self.killWorker(0)
        plugin.onQueueStop(args)
        print '! cmdQueue stopped.'

    def reset(self):
        self.stop()
        self.db.truncate()
        plugin.onQueueReset(args)
        print '! cmdQueue has been reset.'

    def resetJobs(self):
        workers = self.db.getWorkers()
        if len(workers)>0:
            print '! Workers are running, please stop the queue first.'
        else:
            self.db.execute("UPDATE jobs SET status = '%s'" % cqStatus.PENDING)
            print '! Jobs are set to %s' % cqStatus.PENDING

    def listWorkers(self):
        # get workers
        print '! Workers'
        print '! #'.ljust(5), 'PID'.ljust(6), 'Paused?'.ljust(8), 'StartDate'
        workers = self.db.getWorkers()
        for worker in workers:
            print str(worker[0]).ljust(5), str(worker[1]).ljust(6), str(worker[2]).ljust(8), worker[3]
        print '\n',

    def listJobs(self, dfrom, dto, n, status):
        print '! Jobs'
        print '! #'.ljust(5), 'Name'.ljust(10), 'Pid'.ljust(6), 'Status'.ljust(10), 'Priority'.ljust(10), 'SubmitDate'.ljust(22), 'StartDate'.ljust(22), 'FinishDate'.ljust(22), 'Command'

        where = ''
        if status!= 'ALL':
            where = "status='%s'" % status
        
        adst = 'ORDER BY submitdate DESC '
        n = int(n)
        if n>0:
            adst = adst + 'LIMIT %d' % n
        jobs = self.db.getJobs(where, adst)
        
        for job in jobs:
            job = map(lambda x: x if x!=None else '', job)
            print str(job[0]).ljust(5), job[1].ljust(10), str(job[3]).ljust(6), job[7].ljust(10), str(job[8]).ljust(10), job[4].ljust(22), job[5].ljust(22), job[6].ljust(22), job[2]

    def checkWorker(self):
        workers = self.db.getWorkers()
        for worker in workers:
            wpid = worker[1]
            alive = cqUtils.checkWorker(wpid)
            if not alive:
                self.db.deleteWorker(wpid)

    def listdb(self, dfrom, dto, n, status):
        self.listWorkers()
        self.listJobs(dfrom,dto,n, status)
        plugin.onList(dfrom, dto, n, status)
        

    def __del__(self):
        self.db.close()


if __name__ == "__main__":

    __version__ = '1.0.0'
    
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='A command queue system, avaible for *nix, Windows, and maybe OSX')
    parser.add_argument('--config', help='The config file or the config string, default: %(default)s.\n\
If config file path contains no directory separator, script directory will be used.\n\
A config string: db=test.db&workercount=2&interval=60&logfile=cmdQueue.log&loglevel=WARNING\n\
In config file:\n[cmdQueue]\ndb=test.db\nworkercount=2\ninterval=60\nlogfile=cmdQueue.log', default='cmdQueue.conf')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    subparsers = parser.add_subparsers(title='Subcommands', help='<subcommand> -h', dest='command')
    parser_add = subparsers.add_parser('add', help='Add a command into the queue')
    parser_add.add_argument('-n', '--name', required=True)
    parser_add.add_argument('-c', '--cmd', required=True)
    parser_add.add_argument('-p', '--priority', required=True)
    

    parser_list = subparsers.add_parser('list', help='List the workers and jobs')
    parser_list.add_argument('-f', '--frm', help='From which date to show the jobs, default: %(default)s', default=cqUtils.ts2ftime(1))
    parser_list.add_argument('-t', '--to', help='To which date to show the jobs, default: now(%(default)s)', default=cqUtils.ts2ftime())
    parser_list.add_argument('-n', '--number', type=int, help='Limited number of jobs to show, default: %(default)s', default=10)
    parser_list.add_argument('-s', '--status', help='Show jobs with the status (ALL|'+cqStatus.PENDING+'|'+cqStatus.RUNNING+'|'+cqStatus.KILLED+'|'+cqStatus.COMPLETE+'|'+cqStatus.ERROR+', default: %(default)s', default='ALL')
    
    parser_listworkers = subparsers.add_parser('listworkers', help='List the workers')

    parser_listjobs = subparsers.add_parser('listjobs', help='List the jobs')
    parser_listjobs.add_argument('-f', '--frm', help='From which date to show the jobs, default: %(default)s', default=cqUtils.ts2ftime(1))
    parser_listjobs.add_argument('-t', '--to', help='To which date to show the jobs, default: now(%(default)s)', default=cqUtils.ts2ftime())
    parser_listjobs.add_argument('-n', '--number', type=int, help='Limited number of jobs to show, default: %(default)s', default=10)
    parser_listjobs.add_argument('-s', '--status', help='Show jobs with the status (ALL|'+cqStatus.PENDING+'|'+cqStatus.RUNNING+'|'+cqStatus.KILLED+'|'+cqStatus.COMPLETE+'|'+cqStatus.ERROR+', default: %(default)s', default='ALL')
    

    parser_reset = subparsers.add_parser('reset', help='Reset the queue, kill all workers and jobs, and remove them from database')
    parser_reset = subparsers.add_parser('resetjobs', help='Reset all jobs to '+cqStatus.PENDING+' status')

    parser_setup = subparsers.add_parser('setup', help='Setup the queue, create the database tables')

    parser_killjob = subparsers.add_parser('killjob', help='Kill job by pid')
    parser_killjob.add_argument('-p', '--pid', type=int, help='The pid of the job', required=True)

    parser_killjob2 = subparsers.add_parser('killjob2', help='Kill job by id')
    parser_killjob2.add_argument('-i', '--id', type=int, help='The id of the job in database', required=True)

    parser_killWorker = subparsers.add_parser('killworker', help='Kill worker')
    parser_killWorker.add_argument('-p', '--pid', type=int, help='The pid of the worker, default: %(default)s (kill all workers)', default=0)

    parser_start = subparsers.add_parser('start', help='Start all workers')

    parser_stop = subparsers.add_parser('stop', help='Stop all workers, running jobs will not be killed, but no new jobs will run')

    parser_restart = subparsers.add_parser('restart', help='Restart all workers')

    parser_pause = subparsers.add_parser('pause', help='Pause a worker')
    parser_pause.add_argument('-p', '--pid', type=int, help='The pid of the worker, default: %(default)s (pause all workers)', default=0)

    parser_resume = subparsers.add_parser('resume', help='Resume a worker')
    parser_resume.add_argument('-p', '--pid', type=int, help='The pid of the worker, default: %(default)s (resume all workers)', default=0)


    args = parser.parse_args()
    args.db = 'test.db'
    args.workercount = 2
    args.interval =60
    args.logfile = 'cmdQueue.log'
    args.loglevel = 'WARNING'
    # parse config
    if os.path.isfile(args.config):
        cp = ConfigParser.ConfigParser()
        cp.read(args.config)
        if cp.has_option('cmdQueue', 'db'):
            args.db = cp.get('cmdQueue', 'db')
        if cp.has_option('cmdQueue', 'workercount'):
            args.workercount = int(cp.get('cmdQueue', 'workercount'))
        if cp.has_option('cmdQueue', 'interval'):
            args.interval = cp.get('cmdQueue', 'interval')
        if cp.has_option('cmdQueue', 'logfile'):
            args.logfile = cp.get('cmdQueue', 'logfile')
        if cp.has_option('cmdQueue', 'loglevel'):
            args.loglevel = cp.get('cmdQueue', 'loglevel')
    else:
        config = parse_qs(args.config)
        if 'db' in config:
            args.db = config['db'][0]
        if 'workercount' in config:
            args.workercount = int(config['workercount'][0])
        if 'interval' in config:
            args.interval = config['interval'][0]
        if 'logfile' in config:
            args.logfile = config['logfile'][0]
        if 'loglevel' in config:
            args.loglevel = config['loglevel'][0]

    # extend args.db if possible
    if '/' not in args.db and '\\' not in args.db:
        args.db = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.db)
    if '/' not in args.logfile and '\\' not in args.logfile:
        args.logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.logfile)

    plugin = cqPlugin()
    cq = cmdQueue(args)

    if args.command != 'setup':
        cq.checkWorker()
    
    if args.command == 'add':
        job = {
            'name': args.name,
            'cmd': args.cmd,
            'priority': args.priority
        }
        cq.add(job)
        
    elif args.command == 'list':
        cq.listdb(args.frm, args.to, args.number, args.status)

    elif args.command == 'listworkers':
        cq.listWorkers()

    elif args.command == 'listjobs':
        cq.listJobs(args.frm, args.to, args.number, args.status)

    elif args.command == 'setup':
        cq.setup()

    elif args.command == 'killjob':
        cq.killJobByPID(args.pid)

    elif args.command == 'killjob2':
        cq.killJobByID(args.id)

    elif args.command == 'killworker':
        cq.killWorker(args.pid)

    elif args.command == 'stop':
        cq.stop()

    elif args.command == 'restart':
        cq.stop()
    
    elif args.command == 'reset':
        cq.reset()

    elif args.command == 'resetjobs':
        cq.resetJobs()

    elif args.command == 'pause':
        cq.pause(args.pid)

    elif args.command == 'resume':
        cq.resume(args.pid)

    
    # try to starting dead workers
    if args.command in ['start', 'restart']:
        nw = cq.start()
        cq = None # release db connection

        lockFile = os.path.join(gettempdir(), 'cmdQueue-%s.lock' % md5.md5(args.db).hexdigest())
        if os.path.isfile(lockFile):
            os.remove(lockFile)
        
        for i in range(nw):
            cmd = [
                sys.executable,
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cqWorker.py'),
                args.db,
                args.interval,
                args.logfile,
                args.loglevel
            ]
            Popen(cmd)
            

            
