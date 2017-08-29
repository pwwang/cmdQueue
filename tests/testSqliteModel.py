import path, unittest

import sqlite3, time
from os import path, remove
from collections import OrderedDict

from cmdQueue.models.sqlite import sqliteModel
from cmdQueue.model import Model
from cmdQueue.cmdq import cmdQ

cmdq = cmdQ(path.expanduser('~/.cmdQueue/cmdQueue.conf'))
cmdq.reset()

class TestSQLITEModel (unittest.TestCase):
	
	def test0Init(self):
		m = sqliteModel(cmdq)
		self.assertTrue(isinstance(m, sqliteModel))
		self.assertTrue(isinstance(m.conn, sqlite3.Connection))
		self.assertTrue(isinstance(m.cursor, sqlite3.Cursor))
		
	def test_jobTuple2Dict(self):
		job = OrderedDict([
			('id'           , 'ID'),
			('name'         , 'STR'),
			('status'       , 'STR'),
			('pri'          , 'INT'),
			('cmd'          , 'STR'),
			('pid'          , 'INT'),
			('rc'           , 'INT'),
			('starttime'    , 'DATETIME'),
			('submittime'   , 'DATETIME'),
			('completetime' , 'DATETIME')
		])
		self.assertEqual(sqliteModel._jobTuple2Dict(tuple(job.values())), job)
		
	def test_tableExists(self):
		if path.exists(cmdq.config.dbconfig.file):
			remove(cmdq.config.dbconfig.file)
		m = sqliteModel(cmdq)
		self.assertFalse(m._tableExists(Model.TABLENAME_WORKER))
		self.assertFalse(m._tableExists(Model.TABLENAME_JOB))
		
		m._createTable(Model.TABLENAME_WORKER, Model.TABLECOLS_WORKER)
		m._createTable(Model.TABLENAME_JOB, Model.TABLECOLS_JOB)
		
		self.assertTrue(m._tableExists(Model.TABLENAME_WORKER))
		self.assertTrue(m._tableExists(Model.TABLENAME_JOB))
		
		remove(cmdq.config.dbconfig.file)
		self.assertFalse(path.exists(cmdq.config.dbconfig.file))
		
		m = sqliteModel(cmdq)
		
		self.assertFalse(m._tableExists(Model.TABLENAME_WORKER))
		self.assertFalse(m._tableExists(Model.TABLENAME_JOB))
		
		m.createTableIfNotExists()
		self.assertTrue(m._tableExists(Model.TABLENAME_WORKER))
		self.assertTrue(m._tableExists(Model.TABLENAME_JOB))
		
	def test0AddJob(self):
		m = sqliteModel(cmdq)
		m.createTableIfNotExists()
		job = {
			'id'           : None,
			'name'         : 'STR',
			'status'       : 'STR',
			'pri'          : 0,
			'cmd'          : 'sleep 10',
			'pid'          : None,
			'rc'           : None,
			'starttime'    : '',
			'submittime'   : '',
			'completetime' : ''
		}
		ret = m.addJob(job)
		self.assertTrue(isinstance(ret, int))
		
		job = {
			'id'           : None,
			'name'         : 'STR',
			'status'       : 'PENDING',
			'pri'          : 0,
			'cmd'          : 'sleep 10',
			'pid'          : 1,
			'rc'           : None,
			'starttime'    : '',
			'submittime'   : '',
			'completetime' : ''
		}
		m.addJob(job)
	
	def test1GetJobsByName(self):
		m = sqliteModel(cmdq)
		m.createTableIfNotExists()
		jobs = m.getJobsByName("STR")
		self.assertEqual(len(jobs), 2)
		
	def test1GetJobsByPid(self):
		m = sqliteModel(cmdq)
		m.createTableIfNotExists()
		jobs = m.getJobsByPid(1)
		self.assertEqual(len(jobs), 1)
		self.assertEqual(jobs[0]['status'], 'PENDING')
		
	def test1GetJobsByStatus(self):
		m = sqliteModel(cmdq)
		m.createTableIfNotExists()
		jobs = m.getJobsByStatus('PENDING')
		self.assertEqual(len(jobs), 1)
		self.assertEqual(jobs[0]['pid'], 1)
	
	def test2UpdateJobs(self):
		m = sqliteModel(cmdq)
		m.createTableIfNotExists()
		jobs = m.getJobsByName("STR")
		for job in jobs:
			job['pid'] = 1
		m.updateJobs(jobs)
		jobs = m.getJobsByName("STR")
		self.assertEqual(len(jobs), 2)
		self.assertEqual(jobs[0]['pid'], 1)
		self.assertEqual(jobs[1]['pid'], 1)
		
	def test2_safeExec(self):
		import multiprocessing
		
		m = sqliteModel(cmdq)
		m.createTableIfNotExists()
		m.conn.create_function("sleep", 1, time.sleep)
		thr1 = multiprocessing.Process(target = m._safeExec, args = ("SELECT sleep(1.01)", ))
		thr2 = multiprocessing.Process(target = m._safeExec, args = ("SELECT sleep(1.01)", ))
		thr3 = multiprocessing.Process(target = m._safeExec, args = ("SELECT sleep(1.01)", ))
		t    = time.time()
		thr1.start()
		thr2.start()
		thr3.start()
		thr1.join()
		thr2.join()
		thr3.join()
		self.assertTrue( time.time()-t > 3 )
	
	def testUpdateWorker(self):
		m = sqliteModel(cmdq)
		m.createTableIfNotExists()
		self.assertEqual(m.getWorkerPid(), (None, []))
		m.updateWorker(3)
		self.assertEqual(m.getWorkerPid(), (3, []))
		
	def test3DeleteFinishedJobs(self):
		m = sqliteModel(cmdq)
		m.createTableIfNotExists()
		jobs = m.getJobsByName("STR")
		self.assertEqual(len(jobs), 2)
		jobs[0]['status'] = 'COMPLETE'
		m.updateJobs(jobs)
		m.deleteCompletedJobs()
		jobs = m.getJobsByName("STR")
		self.assertEqual(len(jobs), 1)
		
	def testRestoreJobs(self):
		job = [{
			'id'           : None,
			'name'         : 'Restored',
			'status'       : 'PENDING',
			'pri'          : 0,
			'cmd'          : 'sleep 10',
			'pid'          : 1,
			'rc'           : None,
			'starttime'    : '',
			'submittime'   : '',
			'completetime' : ''
		},{
			'id'           : None,
			'name'         : 'Restored',
			'status'       : 'PENDING',
			'pri'          : 0,
			'cmd'          : 'sleep 10',
			'pid'          : 1,
			'rc'           : None,
			'starttime'    : '',
			'submittime'   : '',
			'completetime' : ''
		},{
			'id'           : None,
			'name'         : 'Restored',
			'status'       : 'PENDING',
			'pri'          : 0,
			'cmd'          : 'sleep 10',
			'pid'          : 1,
			'rc'           : None,
			'starttime'    : '',
			'submittime'   : '',
			'completetime' : ''
		}]
		m = sqliteModel(cmdq)
		m.createTableIfNotExists()
		m.restoreJobs(job)
		jobs = m.getJobsByName('Restored')
		self.assertEqual(len(jobs), 3)

if __name__ == '__main__':
	unittest.main(verbosity=2)