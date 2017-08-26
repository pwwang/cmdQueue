import time, os
from subprocess import Popen
from cmdQueue.Utils import getLogger
from cmdQueue.Config import config
logger = getLogger(logfile = config.log.file, loglevel = config.log.level, stream = False)

class Job (object):
	
	def __init__ (self, model, pid = None, id = None, name = '', pri = 0, cmd = '', status = '', rc = None, starttime = '', submittime = '', completetime = ''):
		
		self.model          = model
		self.pid            = pid
		self.id             = id
		self.name           = name
		self.pri            = pri
		self.cmd            = cmd
		self.status         = status if status else self.model.STATUS['submitted']
		self.rc             = rc
		self.starttime      = starttime
		self.submittime     = submittime
		self.completetime   = completetime
		
	def attrs(self):
		return {
			"pid"            : self.pid,
			"id"             : self.id,
			"name"           : self.name,
			"pri"            : self.pri,
			"cmd"            : self.cmd,
			"status"         : self.status,
			"rc"             : self.rc,
			"starttime"      : self.starttime,
			"submittime"     : self.submittime,
			"completetime"   : self.completetime,
		}
		
	def submit(self):
		if not self.submittime:
			self.submittime = time.strftime('%Y-%m-%d %H:%M:%S')
		self.id = self.model.addJob (self.attrs())
		if not self.name:
			self.name = 'Job-%s' % self.id
		return self.name
		
	def run(self):
		self.starttime = time.strftime('%Y-%m-%d %H:%M:%S')
		self.status    = self.model.STATUS['running']
		job = self.attrs()
		self.model.updateJobs([job])
		try:
			logger.info ('Job %s started.' % self.name)
			with open(os.devnull, 'w') as f:
				self.rc       = Popen(self.cmd, shell=True, stdout=f, stderr=f, close_fds=True).wait()
			self.status       = self.model.STATUS['complete']
		except Exception as ex:
			logger.error ('Job %s failed: %s.' % (self.name, str(ex)))
			self.rc           = -1
			self.status       = self.model.STATUS['error']
		self.completetime = time.strftime('%Y-%m-%d %H:%M:%S')
		job = self.attrs()
		self.model.updateJobs([job])
		logger.info ('Job "%s" complete (rc: %s).' % (self.name, self.rc))
		
		