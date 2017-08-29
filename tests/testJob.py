import path, unittest

from os import path
from cmdQueue.cmdq import cmdQ
from cmdQueue.job import Job

class TestJob (unittest.TestCase):
	
	def testInit(self):
		job = {
			'id'           : None,
			'name'         : 'job-1',
			'status'       : 'pending',
			'pri'          : 0,
			'cmd'          : 'sleep 10',
			'pid'          : 1,
			'rc'           : None,
			'starttime'    : '',
			'submittime'   : '',
			'completetime' : ''
		}
	
		j = Job(cmdQ(path.expanduser('~/.cmdQueue/cmdQueue.conf')), **job)
		self.assertTrue(isinstance(j, Job))
		for key in job.keys():
			self.assertEqual(job[key], getattr(j, key))
		
	def testAttrs(self):
		job = {
			'id'           : None,
			'name'         : 'job-1',
			'status'       : 'PENDING',
			'pri'          : 0,
			'cmd'          : 'sleep 10',
			'pid'          : 1,
			'rc'           : None,
			'starttime'    : '',
			'submittime'   : '',
			'completetime' : ''
		}
	
		j = Job(cmdQ(path.expanduser('~/.cmdQueue/cmdQueue.conf')), **job)
		job2 = j.attrs()
		self.assertEqual(job, job2)
		
	def testSubmit(self):
		job = {
			'id'           : None,
			'name'         : None,
			'status'       : 'PENDING',
			'pri'          : 0,
			'cmd'          : 'sleep 3',
			'pid'          : 1,
			'rc'           : None,
			'starttime'    : '',
			'submittime'   : '',
			'completetime' : ''
		}
		j = Job(cmdQ(path.expanduser('~/.cmdQueue/cmdQueue.conf')), **job)
		name = j.submit()
		self.assertEqual(name, 'Job-%s' % j.id)
		jobs = j.cmdq.model.getJobsByName('Job-%s' % j.id)
		self.assertEqual(len(jobs), 1)
		
	def testRun(self):
		job = {
			'id'           : None,
			'name'         : None,
			'status'       : 'PENDING',
			'pri'          : 0,
			'cmd'          : 'bash -c "sleep 3"',
			'pid'          : 1,
			'rc'           : None,
			'starttime'    : '',
			'submittime'   : '',
			'completetime' : ''
		}
		j = Job(cmdQ(path.expanduser('~/.cmdQueue/cmdQueue.conf')), **job)
		j.submit()
		j.run()
		self.assertEqual(j.cmdq.model.getJobsByName('Job-%s' % j.id)[0]['status'], 'COMPLETE')

if __name__ == '__main__':
	unittest.main(verbosity=2)