import path, unittest, tempfile

from cmdQueue.config import Config, DEFAULT_CONFIG

class testConfig (unittest.TestCase):
	
	def testInit(self):
		c = Config()
		self.assertTrue(isinstance(c, Config))		
		self.assertEqual(DEFAULT_CONFIG, c._config)
		
		f = tempfile.NamedTemporaryFile(delete = False)
		f.write('[log]\nlevel: debug'.encode())
		f.close()
		c2 = Config(f.name)
		self.assertEqual(c2._config['log']['level'], 'debug')
		self.assertEqual(c2.log.level, 'debug')
		

if __name__ == '__main__':
	unittest.main(verbosity=2)