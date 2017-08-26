import sqlite3
import time
import json

from ..Model import Model
from ..Lock import lock
from ..Utils import getLogger
from ..Config import config
logger = getLogger(logfile = config.log.file, loglevel = config.log.level, stream = False)

class sqliteModel (Model):
	
	TYPES = {
		'ID'      : 'INTEGER PRIMARY KEY AUTOINCREMENT',
		'INT'     : 'INTEGER',
		'DATETIME': 'TEXT',
		'STR'     : 'TEXT'
	}
	
	def __init__(self, config):
		self.conn   = sqlite3.connect(config.file)
		self.cursor = self.conn.cursor()
	
	@staticmethod
	def _jobTuple2Dict (job):
		ret = {}
		for i, key in enumerate(Model.TABLECOLS_JOB.keys()):
			ret[key] = job[i]
		return ret
		
	@staticmethod
	def _cleanJob(job):
		for key, val in job.items():
			t = Model.TABLECOLS_JOB[key]
			if t in ['ID', 'INT']:
				job[key] = 'NULL' if val is None else str(val)
			else:
				job[key] = json.dumps(val) if not val or (val[0] != '"' and val[-1] != '"') else val
		
	def _safeExec(self, sql):
		lock.acquire()
		try:
			logger.debug('Executing SQL: %s' % sql)
			self.cursor.execute(sql)
			self.conn.commit()
		except Exception as ex:
			logger.error('Failed to executing SQL: %s' % sql)
			logger.error('Error: %s' % str(ex))
			raise
		finally:
			lock.release()
		
	def createTableIfNotExists(self):
		ret = []
		for table, cols in [(Model.TABLENAME_WORKER, Model.TABLECOLS_WORKER), (Model.TABLENAME_JOB, Model.TABLECOLS_JOB)]:
			if not self._tableExists(table):
				self._createTable(table, cols)
				ret.append('Table %s created.' % table)
		return ret
		
	def _createTable(self, table, cols):
		sql = 'CREATE TABLE IF NOT EXISTS %s (' % table
		sql += '  ' + ', \n  '.join([ '%s %s' % (key, self.TYPES[val]) for key, val in cols.items() ])
		sql += ');'
		self._safeExec(sql)
		
	def _tableExists(self, table):
		sql = 'SELECT name FROM sqlite_master WHERE type="table" AND name="%s"' % table
		self._safeExec(sql)
		ret = self.cursor.fetchall()
		return bool(ret)
		
	def getWorkerPid(self):
		sql = 'SELECT pid FROM %s' % (Model.TABLENAME_WORKER)
		self._safeExec(sql)
		ret = self.cursor.fetchone()
		if not ret:
			sql = 'INSERT INTO %s (pid, starttime) VALUES ("", "")' % (Model.TABLENAME_WORKER)
			self._safeExec(sql)
			return None
		return int(ret[0]) if ret[0] else None
		
	def updateWorker(self, pid, starttime = time.strftime('%Y-%m-%d %H:%M:%S')):
		sql = 'UPDATE %s SET starttime = "%s", pid = "%s"' % (Model.TABLENAME_WORKER, starttime, pid)
		self._safeExec(sql)
		self.conn.commit()
		
	def deleteFinishedJobs(self):
		sql = 'DELETE FROM %s WHERE status IN (%s)' % (Model.TABLENAME_JOB, ','.join(['"%s"' % Model.STATUS[k] for k in ['complete', 'error']]))
		self._safeExec(sql)
		
	def restoreJobs(self, jobs):
		raise NotImplementedError()
		
	def getJobsByStatus(self, status):
		sql = 'SELECT * FROM %s WHERE status IN (%s)' % (Model.TABLENAME_JOB, ', '.join(['"%s"' % s for s in status]))
		self._safeExec(sql)
		return map(self._jobTuple2Dict, self.cursor.fetchall())
		
		
	def getJobByName(self, name):
		sql = 'SELECT * FROM %s WHERE name = "%s"' % (Model.TABLENAME_JOB, name)
		self._safeExec(sql)
		return self.cursor.fetchall()
		
	def getJobByPid(self, pid):
		sql = 'SELECT * FROM %s WHERE pid = "%s"' % (Model.TABLENAME_JOB, pid)
		self._safeExec(sql)
		return self.cursor.fetchall()
		
	def updateJobs(self, jobs):
		for job in jobs:
			self._cleanJob(job)
			
			sql = 'UPDATE %s set %s WHERE id = %s' % (
				Model.TABLENAME_JOB,
				', '.join(['%s = %s' % (k,v) for k,v in job.items()]),
				job['id']
			)
			self._safeExec(sql)
		
	def addJob(self, job):
		self._cleanJob(job)
		
		keys, vals = job.keys(), []
		for key in keys:
			vals.append(job[key])
		sql = 'INSERT INTO %s (%s) VALUES (%s)' % (Model.TABLENAME_JOB, ', '.join(keys), ', '.join(vals))
		self._safeExec(sql)
		job['id'] = self.cursor.lastrowid
		if not job['name'] or job['name'] == '""':
			job['name'] = 'Job-%s' % job['id']
		print job
		self.updateJobs([job])
		return job['id']
		
	def __del__(self):
		self.cursor.close()
		self.cursor=None
		self.conn.close()
		self.conn = None