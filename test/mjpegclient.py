"""
Created on Apr 12, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import unittest, sys, logging, codeferm.config, codeferm.mjpegclient


class mjpegclient(unittest.TestCase):


    def setUp(self):
        # sys.argv[6] is configuration file or default is used
        if len(sys.argv) < 7:
            fileName = "../config/test.ini"
        else:
            fileName = sys.argv[6]
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
        self.client = codeferm.mjpegclient.mjpegclient("http://gasparillamarina.dyndns.org:6812/cam_1.cgi", self.appConfig.socketTimeout)

    def tearDown(self):
        self.logger.debug("tearDown")
        self.client.close()

    def testDecode(self):
        self.logger.debug("testDecode")
        frame = self.client.getFrame()
        # Make sure we have image data
        self.assertTrue(frame, "Frame cannot be empty")
        self.logger.debug("Frame size: %d" % len(frame))        
        image = self.client.decodeFrame(frame)
        # Make sure we have image data
        self.assertFalse(image.size == 0, "Image cannot be size 0")
        self.logger.debug("Height: %d, width: %d, fps: %d" % (self.client.frameHeight, self.client.frameWidth, self.client.fps))
        
if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])
