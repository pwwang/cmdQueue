import sqlite3
import time
import json
import filelock

from ..model import Model
from ..utils import getLogger

class sqliteModel (Model):
	
	TYPES = {
		'ID'      : 'INTEGER PRIMARY KEY AUTOINCREMENT',
		'INT'     : 'INTEGER',
		'DATETIME': 'TEXT',
		'STR'     : 'TEXT'
	}
	
	def __init__(self, cmdq):
		self.cmdq   = cmdq
		self.conn   = sqlite3.connect(cmdq.config.dbconfig.file)
		self.cursor = self.conn.cursor()
		self.logger = getLogger(logfile = cmdq.config.log.file, loglevel = cmdq.config.log.level, stream = False)
	
	@staticmethod
	def _jobTuple2Dict (job):
		ret = {}
		for i, key in enumerate(Model.TABLECOLS_JOB.keys()):
			ret[key] = job[i]
		return ret
		
	def _safeExec(self, sql, data = None):
		if data is None: data = ()
		lock = filelock.FileLock(self.cmdq.config.dbconfig.lock)
		lock.acquire()
		try:
			self.logger.debug('Executing SQL: %s' % sql)
			self.logger.debug('  With data: %s' % str(data))
			self.cursor.execute(sql, data)
			self.conn.commit()
		except Exception as ex:
			self.logger.error('  Failed: %s' % str(ex))
			self.logger.error('  With data: %s' % str(data))
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
		sql = 'SELECT pid, workers FROM %s' % (Model.TABLENAME_WORKER)
		self._safeExec(sql)
		ret = self.cursor.fetchone()
		if not ret:
			sql = 'INSERT INTO %s (pid, starttime, workers) VALUES ("", "", "")' % (Model.TABLENAME_WORKER)
			self._safeExec(sql)
			return (None, [])
		return (
			None if not ret[0] else int(ret[0]), 
			[] if not ret[1] else list(map(int, ret[1].split(',')))
		) if ret else (None, [])
		
	def updateWorker(self, pid = None, workers = None):
		sets = []
		if pid is not None:
			sets.append('pid = "%s"' % str(pid))
		if workers is not None:
			sets.append('workers = "%s"' % (",".join(list(map(str, workers)))))
		sets.append('starttime = "%s"' % time.strftime('%Y-%m-%d %H:%M:%S'))
		sql = 'UPDATE %s SET %s' % (Model.TABLENAME_WORKER, ', '.join(sets))
		self._safeExec(sql)
		
	def deleteCompletedJobs(self):
		sql = 'DELETE FROM %s WHERE status IN (%s)' % (Model.TABLENAME_JOB, ','.join(['"%s"' % Model.STATUS[k] for k in ['complete', 'error']]))
		self._safeExec(sql)
		
	def restoreJobs(self, jobs):
		for job in jobs:
			self.addJob(job)
		
	def getJobsByStatus(self, status = []):
		if not isinstance(status, list):
			status = [status]
		if not status:
			sql = 'SELECT * FROM %s' % (Model.TABLENAME_JOB)
		else:
			sql = 'SELECT * FROM %s WHERE status IN (%s)' % (Model.TABLENAME_JOB, ', '.join(['"%s"' % s for s in status]))
		self._safeExec(sql)
		return list(map(self._jobTuple2Dict, self.cursor.fetchall()))
		
	def getJobsByName(self, name):
		sql = 'SELECT * FROM %s WHERE name = ?' % (Model.TABLENAME_JOB)
		self._safeExec(sql, (name, ))
		return list(map(self._jobTuple2Dict, self.cursor.fetchall()))
		
	def getJobsByPid(self, pid):
		sql = 'SELECT * FROM %s WHERE pid = ?' % (Model.TABLENAME_JOB)
		self._safeExec(sql, (pid, ))
		return list(map(self._jobTuple2Dict, self.cursor.fetchall()))
		
	def updateJobs(self, jobs):
		for job in jobs:
			#self._cleanJob(job)
			keys = job.keys()
			sql = 'UPDATE %s SET %s WHERE id = %s' % (
				Model.TABLENAME_JOB,
				', '.join(['%s = ?' % k for k in keys]),
				job['id']
			)
			self._safeExec(sql, [job[k] for k in keys])
		
	def addJob(self, job):
		#self._cleanJob(job)
		
		keys, vals = job.keys(), []
		for key in keys:
			vals.append(job[key])
		sql = 'INSERT INTO %s (%s) VALUES (%s)' % (Model.TABLENAME_JOB, ', '.join(keys), ', '.join(['?']* len(vals)))
		self._safeExec(sql, vals)
		job['id'] = self.cursor.lastrowid
		if not job['name'] or job['name'] == '""':
			job['name'] = 'Job-%s' % job['id']
		self.updateJobs([job])
		return int(job['id'])
		
	def reset(self):
		sql = 'DROP TABLE IF EXISTS %s' % Model.TABLENAME_JOB
		self._safeExec(sql)
		sql = 'DROP TABLE IF EXISTS %s' % Model.TABLENAME_WORKER
		self._safeExec(sql)
		
	def __del__(self):
		self.cursor.close()
		self.cursor=None
		self.conn.close()
		self.conn = None