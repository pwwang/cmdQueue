from collections import OrderedDict

class Model (object):
	
	TABLENAME_WORKER = 'cmdq_worker'
	TABLECOLS_WORKER = OrderedDict([
		('id'        , 'ID'),
		('pid'       , 'INT'),
		('starttime' , 'DATETIME'),
		('workers'   , 'STR')
	])
	
	TABLENAME_JOB = 'cmdq_job'
	TABLECOLS_JOB = OrderedDict([
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
	STATUS = {
		'submitted': 'SUBMITTED',
		'pending'  : 'PENDING',
		'running'  : 'RUNNING',
		'complete' : 'COMPLETE',
		'error'    : 'ERROR'
	}
	
	def __init__(self, cmdq):
		raise NotImplementedError()
		
	def createTableIfNotExists(self):
		raise NotImplementedError()
	
	def _createTable(self, table):
		raise NotImplementedError()
	
	def _tableExists(self, table):
		raise NotImplementedError()
		
	def getWorkerPid(self):
		raise NotImplementedError()
		
	def updateWorker(self, pid = None, workers = None):
		raise NotImplementedError()
		
	def deleteCompletedJobs(self):
		raise NotImplementedError()
		
	def restoreJobs(self, jobs):
		raise NotImplementedError()
		
	def getJobsByStatus(self, status = []):
		raise NotImplementedError()
		
	def getJobsByName(self, name):
		raise NotImplementedError()
		
	def getJobsByPid(self, pid):
		raise NotImplementedError()
		
	def updateJobs (self, jobs):
		raise NotImplementedError()		
		
	def addJob(self, job):
		raise NotImplementedError()
		
	def reset(self):
		raise NotImplementedError()
	