## config file: ~/.cmdQueue/cmdQueue.conf
## [general]
## workers  = 10 
## interval = 10
## database = sqlite
## 
## [log] 
## file = /paht/to/logfile
## level = info
##
## [dbconfig]
## file = /path/to/database
from os import path, makedirs
from . import Utils
try:
	from ConfigParser import ConfigParser
except ImportError:
	# Python 2 and 3 (after ``pip install configparser``):
	from configparser import ConfigParser

CONFIG_FILE    = path.expanduser('~/.cmdQueue/cmdQueue.conf')
DEFAULT_CONFIG = {
	'general': {
		'workers':  10,
		'interval': 10,
		'database': 'sqlite',
		'lockfile': '~/.cmdQueue/cmdQueue.lock'
	},
	'log': {
		'file':  '~/.cmdQueue/cmdQueue.log',
		'level': 'info'
	},
	'dbconfig': {
		'file': '~/.cmdQueue/cmdQueue.db'
	}
}

class Config(object):
	
	def __init__(self, configfile):
		self._config = DEFAULT_CONFIG
		if path.exists(configfile):
			cp = ConfigParser()
			cp.read(configfile)
			Utils.dictUpdate(self._config, cp._sections)

		self._setattrs()
		
		
	def _setattrs(self):
		for key, val in self._config.items():
			setattr(self, key, lambda: val)
			for k, v in val.items():
				if k == 'file' or k == 'lockfile':
					v = path.expanduser(v)
					if not path.exists(path.dirname(v)):
						makedirs(path.dirname(v))
				setattr(getattr(self, key), k, v)
	
config = Config(CONFIG_FILE)