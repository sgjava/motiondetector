"""
Created on Apr 13, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import re, cv2, framebase

class videocapture(framebase.framebase):
    """cv2.VideoCapture based frame grabber.
    
    It's probably a good idea to start with this plugin as default since it's
    part of the OpenCV package. If you run into issues (like it dying
    without error or hanging) then use one of the other plugins.   

    """
    
    def __init__(self, url):
        """Open stream"""
        # Check for int regex
        intRe = re.compile(r"^[-]?\d+$")
        # If url is int then open USB camera
        if intRe.match(str(url)) is not None:
            self.capture = cv2.VideoCapture(int(url))
        else:
            self.capture = cv2.VideoCapture(url)
        self.frameHeight = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frameWidth = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = int(self.capture.get(cv2.CAP_PROP_FPS))
        
    def setProperties(self, properties):
        """ Set VideoCapture properties """
        if properties != None:
            for item in properties:
                self.capture.set(item[0], item[1])
        
    def getFrame(self):
        """ Read in image. Sometimes you will see 
        "GStreamer-CRITICAL **: gst_caps_unref: assertion `caps != NULL" failed"
        error which can usually be ignored. On some cameras VideoCapture just
        dies without error. In that case try one of the other plugins."""
        s, image = self.capture.read()
        return image
   
    def decodeFrame(self, image):
        """ cv2.VideoCapture will not return a raw image, so we just return the decoded image passed """
        return image
   
    def close(self):
        """ Clean up resources """
        self.capture.release()
