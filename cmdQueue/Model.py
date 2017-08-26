from collections import OrderedDict

class Model (object):
	
	TABLENAME_WORKER = 'cmdq_worker'
	TABLECOLS_WORKER = OrderedDict([
		('id'        , 'ID'),
		('pid'       , 'INT'),
		('starttime' , 'DATETIME')
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
		'complete' : 'COMPELTE',
		'error'    : 'ERROR'
	}
	
	def __init__(self, config):
		raise NotImplementedError()
		
	def createTableIfNotExists(self):
		raise NotImplementedError()
	
	def _createTable(self, table):
		raise NotImplementedError()
	
	def _tableExists(self, table):
		raise NotImplementedError()
		
	def getWorkerPid(self):
		raise NotImplementedError()
		
	def updateWorker(self, pid, starttime):
		raise NotImplementedError()
		
	def deleteFinishedJobs(self):
		raise NotImplementedError()
		
	def restoreJobs(self, jobs):
		raise NotImplementedError()
		
	def getJobsByStatus(self, status):
		raise NotImplementedError()
		
	def getJobByName(self, name):
		raise NotImplementedError()
		
	def getJobByPid(self, pid):
		raise NotImplementedError()
		
	def updateJobs (self, jobs):
		raise NotImplementedError()		
		
	def addJob(self, job):
		raise NotImplementedError()
		
	def __del__(self):
		raise NotImplementedError()