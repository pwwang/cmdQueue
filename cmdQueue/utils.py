"""
Utils
"""
import logging
from subprocess import Popen
from os import devnull
import warnings
	
def pidIsAlive (pid):
	warnings.simplefilter("ignore")
	cmd = ['kill', '-s', '0', str(pid)]
	with open(devnull, 'w') as f:
		return Popen(cmd, stdout = f, stderr = f).wait() == 0
		
def pidKill (pid):
	warnings.simplefilter("ignore")
	cmd = ['kill', '-s', '9', str(pid)]
	with open(devnull, 'w') as f:
		return Popen(cmd, stdout = f, stderr = f).wait() == 0

def cmdStart (cmd):
	warnings.simplefilter("ignore")
	return Popen(cmd, stdout=None, stderr=None, close_fds=True).pid

def dictUpdate(origDict, newDict):
	"""
	Update a dictionary recursively. 
	@params:
		`origDict`: The original dictionary
		`newDict`:  The new dictionary
	@examples:
		```python
		od1 = {"a": {"b": {"c": 1, "d":1}}}
		od2 = {key:value for key,value in od1.items()}
		nd  = {"a": {"b": {"d": 2}}}
		od1.update(nd)
		# od1 == {"a": {"b": {"d": 2}}}, od1["a"]["b"] is lost
		dictUpdate(od2, nd)
		# od2 == {"a": {"b": {"c": 1, "d": 2}}}
		```
	"""
	for k, v in newDict.items():
		if not isinstance(v, dict) or not k in origDict or not isinstance(origDict[k], dict):
			origDict[k] = newDict[k]
		else:
			dictUpdate(origDict[k], newDict[k])
			
def getLogger(logfile, loglevel = 'info', stream = True):
	formatter = logging.Formatter("[%(asctime)s][%(levelname)7s] %(module)s: %(message)s")
	logger    = logging.getLogger ('cmdQueue')
	for handler in logger.handlers:
		handler.close()
	logger.handlers = []
	fileCh = logging.FileHandler(logfile)
	fileCh.setFormatter(formatter)
	logger.addHandler (fileCh)
	
	if stream:
		streamCh  = logging.StreamHandler()
		streamCh.setFormatter(formatter)
		logger.addHandler(streamCh)
			
	logger.setLevel(loglevel.upper())
	return logger
