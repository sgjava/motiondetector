'''
Created on Apr 12, 2017

@author: sgoldsmith
'''
import unittest, sys, logging, codeferm.config


class mjpegclient(unittest.TestCase):


    def setUp(self):
        if len(sys.argv) < 7:
            fileName = "../config/test.ini"
        else:
            fileName = sys.argv[6]
        print "fileName: %s" % fileName      
        self.appConfig = codeferm.config.config(fileName)
        # Set up logger
        self.logger = logging.getLogger("mjpegclient")
        self.logger.setLevel(self.appConfig.loggingLevel)
        formatter = logging.Formatter(self.appConfig.loggingFormatter)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info("Configuring from file: %s" % fileName)
        self.logger.info("Logging level: %s" % self.appConfig.loggingLevel)
        self.logger.debug("Logging formatter: %s" % self.appConfig.loggingFormatter)

    def tearDown(self):
        pass


    def testName(self):
        pass


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])