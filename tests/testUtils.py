import path, unittest, tempfile, sys
from time import sleep
from cmdQueue import utils

from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
	
@contextmanager
def captured_output():
	new_out, new_err = StringIO(), StringIO()
	old_out, old_err = sys.stdout, sys.stderr
	try:
		sys.stdout, sys.stderr = new_out, new_err
		yield sys.stdout, sys.stderr
	finally:
		sys.stdout, sys.stderr = old_out, old_err

class Testutils (unittest.TestCase):
	def testCmdStart(self):
		pid = utils.cmdStart(['bash', '-c', 'sleep 1'])
		self.assertTrue (utils.pidIsAlive(pid))
		sleep(1.1)
		self.assertFalse (utils.pidIsAlive(pid))
		
	def testPidKill(self):
		pid = utils.cmdStart(['bash', '-c', 'sleep 1'])
		self.assertTrue (utils.pidIsAlive(pid))
		self.assertTrue (utils.pidIsAlive(pid))
		utils.pidKill(pid)
		self.assertFalse (utils.pidIsAlive(pid))
	
	def testDictUpdate(self):
		od1 = {"a": {"b": {"c": 1, "d":1}}}
		od2 = {key:value for key,value in od1.items()}
		nd  = {"a": {"b": {"d": 2}}}
		od1.update(nd)
		self.assertEqual(od1, {"a": {"b": {"d": 2}}})
		
		utils.dictUpdate(od2, nd)
		self.assertEqual(od2, {"a": {"b": {"c":1, "d": 2}}})
		
	def testGetLogger(self):
		
		with tempfile.NamedTemporaryFile() as f, captured_output() as (out, err):
			logger1 = utils.getLogger(f.name, stream=False)
			logger1.info('test log1')
			self.assertTrue('[   INFO] testUtils: test log1' in str(f.read()))
			self.assertFalse('[   INFO] testUtils: test log1' in out.getvalue())
			logger2 = utils.getLogger(f.name, stream = True)
			logger2.info('test log2')
			self.assertTrue('[   INFO] testUtils: test log2' in str(f.read()))
		self.assertTrue('[   INFO] testUtils: test log2' in err.getvalue())
		self.assertFalse('[   INFO] testUtils: test log1' in err.getvalue())
	
if __name__ == '__main__':
	unittest.main(verbosity=2)