from os import path, remove
from importlib import import_module
from sys import executable, path as syspath
from time import sleep
from .config import Config
from .plugin import Plugin
from . import utils

class cmdQ (object):

	def __init__ (self, configfile):
		
		self.config = Config(configfile)
		self.logger = utils.getLogger(logfile = self.config.log.file, loglevel = self.config.log.level, stream = True)
		modelname   = self.config.general.database + 'Model'
		model       = import_module('.models.%s' % self.config.general.database, __package__)
		self.model  = getattr(model, modelname)(self)
		msgs = self.model.createTableIfNotExists()
		if msgs:
			for msg in msgs:
				self.logger.info (msg)
		
		self.workerbin = [path.join(path.dirname(path.dirname(path.realpath(__file__))), 'bin', 'cqworker'), configfile]
		self.workerpid, self.workers = self.model.getWorkerPid()
		
		self.plugins = self.getPlugins()
		Plugin.call(self.plugins, 'onQueueInit')
		
	def isWorkerAlive (self):
		if self.workerpid is None:
			return False
		return utils.pidIsAlive(self.workerpid)
		
	def stopWorker (self):
		if self.isWorkerAlive():
			self.logger.info('Stoping worker (PID %s) ...' % self.workerpid)
			for w in self.workers:
				r = utils.pidKill(w)
				if not r:
					self.logger.warning ('  Failed to stop subworker (PID: %s).' % w)
				else:
					self.logger.info ('  Subworker (PID: %s) stopped.' % w)
			r = utils.pidKill (self.workerpid)
			if not r:
				self.logger.warning ('  Failed to stop worker (PID: %s).' % self.workerpid)
			else:
				self.logger.info ('  Worker (PID: %s) stopped.' % self.workerpid)
			self.model.updateWorker(pid = None, workers = [])
			Plugin.call(self.plugins, 'onStopWorker')
		else:
			self.logger.info ('Worker (PID: %s) is not running.' % self.workerpid)
			
	def startWorker (self):
		if self.isWorkerAlive():
			self.logger.warning ('Worker (PID: %s) is already running.' % self.workerpid)
		else:
			cmd = [executable]
			cmd.extend(self.workerbin)
			self.workerpid = utils.cmdStart(cmd)
			self.logger.info ('Try to start worker started at: %s' % self.workerpid)
			# let cqworker update worker in database
			sleep (.5)
			self.workerpid, self.workers = self.model.getWorkerPid()
			self.logger.info ('Worker started at: %s' % self.workerpid)
			self.logger.info ('  Subworkers started at: %s' % self.workers)
			Plugin.call(self.plugins, 'onStartWorker')
		
	def archive (self, outfile):
		doneJobs = self.model.getJobsByStatus([self.model.STATUS['complete'], self.model.STATUS['error']])
		# write header
		cols = self.model.TABLECOLS_JOB
		with open(outfile, 'w') as fout:
			fout.write("#" + "\t".join(cols) + "\n")
			for job in doneJobs:
				fout.write("\t".join(list(map(str, [job[key] for key in cols]))) + "\n")
		self.logger.info ('Completed/Error jobs archived to "%s".' % outfile)
		self.model.deleteCompletedJobs()
		self.logger.info ('Completed/Error jobs are removed from database.')
	
	def restore (self, infile):
		# read jobs from infile
		cols = []
		doneJobs = []
		with open(infile) as fin:
			for line in fin:
				line  = line.strip()
				if not line: continue
				parts = line.split("\t")
				if line.startswith('#'):
					parts[0] = parts[0][1:]
					cols = parts
				else:
					doneJobs.append({cols[i]:part for i, part in enumerate(parts)})
		self.model.restoreJobs(doneJobs)
		self.logger.info ('Jobs from "%s" restored.' % infile)
		
	def reset (self):
		self.stopWorker()
		self.model.reset()
		self.logger.info ('Database reset.')
		remove (self.config.log.file)
		self.logger.info ('Log file removed.')
		
	def workerInfo (self):
		ret = ''
		if self.isWorkerAlive():
			ret += 'Worker is running at: %s\n' % self.workerpid
			ret += 'Subworkers are running at: %s\n' % (', '.join(list(map(str, self.workers))))
		else:
			ret += 'Worker is not running.\n'
		ret += 'Number of subworkers: %s.\n' % self.config.general.nworkers
		ret += 'Jobs are pulled every %s seconds.\n' % self.config.general.interval
		return ret
		
	def listJobs(self, status = []):
		jobs = self.model.getJobsByStatus(status)
		Plugin.call(self.plugins, 'onListJobs', jobs = jobs)
		return jobs
	
	def getPlugins(self):
		ret = []
		pluginnames = self.config.general.plugins
		for name in pluginnames:
			pname = name + 'Plugin'
			if pname not in self.config._config:
				pdir = path.join(path.dirname(path.realpath(__file__)), 'plugins')
			elif 'dir' in self.config._config[pname]:
				pdir = self.config._config[pname]['dir']
			syspath.append(pdir)
			pluginClass = getattr(import_module(name), pname)
			plugin = pluginClass(self, name)
			ret.append(plugin)
			self.logger.info('Plugin loaded: %s' % name)
		return sorted(ret, key = lambda x: x.priority)