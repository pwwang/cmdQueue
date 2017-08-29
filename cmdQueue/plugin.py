from os import path

class Plugin(object):
	
	def __init__(self, cmdq, name, priority = 0):
		self.cmdq     = cmdq
		self.priority = priority
		self.name     = name
		self.config   = {} if name + 'Plugin' not in cmdq.config._config else cmdq.config._config[name + 'Plugin']
		
	def onQueueInit(self):
		pass
		
	def onStopWorker(self):
		pass
		
	def onStartWorker(self):
		pass
		
	def onListJobs(self, jobs):
		pass
		
	def onJobEnqueue(self, job):
		pass
		
	def onJobStart(self, job):
		pass
		
	def onJobEnd(self, job):
		pass
		
	def onJobsPulled(self, jobs):
		pass
		
	def onJobInit(self, job):
		pass
		
	def onJobSubmit(self, job):
		pass
		
	@staticmethod
	def call(plugins, func, *args, **kwargs):
		for plugin in plugins:
			getattr(plugin, func)(*args, **kwargs)