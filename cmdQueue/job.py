import time, os
from subprocess import Popen
from cmdQueue.utils import getLogger
from cmdQueue.plugin import Plugin

class Job (object):
	
	def __init__ (self, cmdq, pid = None, id = None, name = '', pri = 0, cmd = '', status = '', rc = None, starttime = '', submittime = '', completetime = ''):
		
		self.cmdq           = cmdq
		self.pid            = pid
		self.id             = id
		self.name           = name
		self.pri            = pri
		self.cmd            = cmd
		self.status         = status if status else self.cmdq.model.STATUS['submitted']
		self.rc             = rc
		self.starttime      = starttime
		self.submittime     = submittime
		self.completetime   = completetime
		self.logger = getLogger(logfile = self.cmdq.config.log.file, loglevel = self.cmdq.config.log.level, stream = False)
		Plugin.call(self.cmdq.plugins, 'onJobInit', job = self.attrs())
		
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
		self.id = self.cmdq.model.addJob (self.attrs())
		if not self.name:
			self.name = 'Job-%s' % self.id
		Plugin.call(self.cmdq.plugins, 'onJobSubmit', job = self.attrs())
		return self.name
		
	def run(self):
		self.starttime = time.strftime('%Y-%m-%d %H:%M:%S')
		self.status    = self.cmdq.model.STATUS['running']
		
		try:
			self.logger.info ('Job %s started.' % self.name)
			with open(os.devnull, 'w') as f:
				p        = Popen(self.cmd, shell=True, stdout=f, stderr=f, close_fds=True)
				self.pid = p.pid
				job      = self.attrs()
				self.cmdq.model.updateJobs([job])
				self.rc  = p.wait()
			self.status       = self.cmdq.model.STATUS['complete']
		except Exception as ex:
			self.logger.error ('Job %s failed: %s.' % (self.name, str(ex)))
			self.rc           = -1
			self.status       = self.cmdq.model.STATUS['error']
		self.completetime = time.strftime('%Y-%m-%d %H:%M:%S')
		job = self.attrs()
		self.cmdq.model.updateJobs([job])
		self.logger.info ('Job "%s" complete (rc: %s).' % (self.name, self.rc))
		
		