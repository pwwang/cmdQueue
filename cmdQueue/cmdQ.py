from os import path
from importlib import import_module
from sys import executable
from .Config import config
from . import Utils

logger = Utils.getLogger(logfile = config.log.file, loglevel = config.log.level)

class cmdQ (object):

	def __init__ (self):
		
		modelname   = config.general.database + 'Model'
		model       = import_module('.databases.%s' % modelname, __package__)
		self.model  = getattr(model, modelname)(config.dbconfig)
		msgs = self.model.createTableIfNotExists()
		if msgs:
			for msg in msgs:
				logger.info (msg)
		
		self.workerbin = path.join(path.dirname(path.dirname(path.realpath(__file__))), 'bin', 'cqworker')
		self.workerpid = self.model.getWorkerPid()
		
	def isWorkerAlive (self):
		if self.workerpid is None:
			return False
		
		return Utils.pidIsAlive(self.workerpid)
		
	def stopWorker (self):
		if self.isWorkerAlive():
			r = Utils.pidKill (self.workerpid)
			if not r:
				logger.error ('Failed to stop worker (PID: %s).' % self.workerpid)
			else:
				logger.error ('Worker (PID: %s) stopped.' % self.workerpid)
				#self.model.stopRunningJobs()
		else:
			logger.info ('Worker (PID: %s) is not running.' % self.workerpid)
			
	def startWorker (self):
		if self.isWorkerAlive():
			logger.warning ('Worker (PID: %s) is already running.' % self.workerpid)
		else:
			cmd = [executable, self.workerbin]
			self.workerpid = Utils.cmdStart(cmd)
			logger.info ('Worker started: %s' % self.workerpid)
			self.model.updateWorker (self.workerpid)
		
	def archive (self, outfile):
		doneJobs = self.model.getFinishedJobs()
		self.model.deleteFinishedJobs()
		logger.info ('Completed/Error jobs are removed from database.')
		# write doneJobs to outfile
	
	def restore (self, infile):
		# read jobs from infile
		doneJobs = None
		self.model.restoreJobs(doneJobs)
		
	def workerInfo (self):
		ret = ''
		if self.isWorkerAlive():
			ret += 'Worker is running: %s\n' % self.workerpid
		else:
			ret += 'Worker is not running.\n'
		ret += 'Number of workers: %s.\n' % config.general.workers
		ret += 'Jobs are pulled every %s seconds.\n' % config.general.interval
		return ret
		
	def listJobs(self, status):
		jobs = self.model.getJobsByStatus(status)
		return jobs
	
cmdq = cmdQ()