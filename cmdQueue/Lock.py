from os import path, remove
from time import sleep
from .Config import config

class LockException (Exception):
	pass

class Lock (object):
	
	def __init__(self, lockfile, timeout = 10):
		self.lockfile = lockfile
		self.timeout  = timeout
		
	def acquire(self):
		timeout = self.timeout
		while True:
			if not path.exists(self.lockfile):
				self.tryAcquire()
				break
			else:
				sleep(1)
				timeout -= 1
		if timeout <= 0:
			raise LockException('Timeout to acquire lock.')
			
	def release(self):
		timeout = self.timeout
		while True:
			if path.exists(self.lockfile):
				self.tryRelease()
				break
			else:
				sleep(1)
				timeout -= 1
		if timeout <= 0:
			raise LockException('Timeout to release lock.')
		
	def tryAcquire(self):
		open(self.lockfile, 'w').close()
		
	def tryRelease(self):
		remove(self.lockfile)
		
	def __enter__(self):
		self.acquire()
		
	def __exit__(self, t, e, tb):
		self.release()

lock = Lock(config.general.lockfile)