from cmdQueue.plugin import Plugin

class samplePlugin(Plugin):
	
	def onQueueInit(self):
		self.cmdq.logger.info('Queue started!')
		
	def onJobInit(self, job):
		self.cmdq.logger.info('Job initiated: %s' % job)
		