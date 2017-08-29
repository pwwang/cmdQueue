import path, unittest

import tempfile
from os import path

from cmdQueue.cmdq import cmdQ
from cmdQueue.models.sqlite import sqliteModel

class TestModel (unittest.TestCase):
	
	def testInit(self):
		cmdq = cmdQ(path.expanduser('~/.cmdQueue/cmdQueue.conf'))
		self.assertTrue (isinstance(cmdq, cmdQ))
		self.assertTrue (isinstance(cmdq.model, sqliteModel))
		self.assertEqual(cmdq.workerbin, [path.join(path.dirname(path.dirname(path.realpath(__file__))), 'bin', 'cqworker'), path.expanduser('~/.cmdQueue/cmdQueue.conf')])
		#self.assertEqual(cmdq.workerpid, None)
		
	def testStartWorker(self):
		cmdq = cmdQ(path.expanduser('~/.cmdQueue/cmdQueue.conf'))
		cmdq.stopWorker()
		cmdq.startWorker()
		self.assertTrue(cmdq.isWorkerAlive())
		self.assertEqual(cmdq.workerInfo(), 'Worker is running at: %s\nSubworkers are running at: %s\nNumber of subworkers: %s.\nJobs are pulled every %s seconds.\n' % (cmdq.workerpid, ', '.join(list(map(str, cmdq.workers))), cmdq.config.general.nworkers, cmdq.config.general.interval))
		cmdq.stopWorker()
		self.assertFalse(cmdq.isWorkerAlive())
		self.assertEqual(cmdq.workerInfo(), 'Worker is not running.\nNumber of subworkers: %s.\nJobs are pulled every %s seconds.\n' % (cmdq.config.general.nworkers, cmdq.config.general.interval))
		
	def testListJobs(self):
		cmdq = cmdQ(path.expanduser('~/.cmdQueue/cmdQueue.conf'))
		jobs = cmdq.listJobs()
		self.assertTrue(len(jobs) >= 0)
		with tempfile.NamedTemporaryFile() as f:
			cmdq.archive(f.name)
			jobs2 = cmdq.listJobs()
			self.assertTrue(len(jobs2) <= len(jobs))
			cmdq.restore(f.name)
			jobs3 = cmdq.listJobs()
			self.assertTrue(len(jobs3) <= len(jobs2))

if __name__ == '__main__':
	unittest.main(verbosity=2)