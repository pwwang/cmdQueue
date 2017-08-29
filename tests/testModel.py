import path, unittest

from cmdQueue.model import Model

class TestModel (unittest.TestCase):
	
	def testInit(self):
		self.assertRaises(NotImplementedError, Model, None)
			
	def testConstants(self):
		
		self.assertEqual (Model.TABLENAME_WORKER, 'cmdq_worker')
		self.assertEqual (list(Model.TABLECOLS_WORKER.items()), [
			('id'        , 'ID'),
			('pid'       , 'INT'),
			('starttime' , 'DATETIME'),
			('workers'   , 'STR')
		])
		self.assertEqual (Model.TABLENAME_JOB, 'cmdq_job')
		self.assertEqual (list(Model.TABLECOLS_JOB.items()), [
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

if __name__ == '__main__':
	unittest.main(verbosity=2)