import logging


def onJobSubmit(jobid, jobname, jobcmd):
    print '! [PLUGIN: SAMPLE] Add job: %s(%d) [%s]' % (jobname, jobid, jobcmd)

def onSetup():
    print '! [PLUGIN: SAMPLE] cmdQueue set up.'

def onJobKill(jobid, jobpid, jobname, jobcmd):
    print '! [PlUGIN: SAMPLE] Job %s(%d) at PID %d killed [%s]' % (jobname, jobid, jobpid, jobcmd)
    
def onWorkerKill(wpid):
    print '! [PLUGIN: SAMPLE] Worker %d killed.' % wpid

def onWorkerPause(wpid):
    print '! [PLUGIN: SAMPLE] Worker %d paused.' % wpid

def onWorkerResume(wpid):
    print '! [PLUGIN: SAMPLE] Worker %d resumed.' % wpid

def onQueueStart(args):
    print '! [PLUGIN: SAMPLE] Queue started: ', vars(args)

def onQueueStop(args):
    print '! [PLUGIN: SAMPLE] Queue stopped: ', vars(args)

def onQueueReset(args):
    print '! [PLUGIN: SAMPLE] Queue reset: ', vars(args)

def onList(dfrom, dto, n, status):
    print '! [PLUGIN: SAMPLE] List %d %s jobs from %s to %s' % (n, status, dfrom, dto)

''' Logging available to the logfile '''
def onWorkerStart(wpid):
    logging.info('[PLUGIN: SAMPLE] Worker %d started.', wpid)

def onJobStart(jobid, jobcmd):
    logging.info('[PLUGIN: SAMPLE] Job %d started: [%s]', jobid, jobcmd)

def onJobEnd(jobid, jobcmd):
    logging.info('[PLUGIN: SAMPLE] Job %d ended: [%s]', jobid, jobcmd)




