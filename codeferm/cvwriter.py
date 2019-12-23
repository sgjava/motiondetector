"""
Created on Apr 12, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import cv2, writerbase


class cvwriter(writerbase.writerbase):
    """Video writer based on OpenCV VideoWriter.
    
    Encode single numpy image as video frame.

    """
    
    def __init__(self, fileName, vcodec, fps, frameWidth, frameHeight):
        self.videoWriter = cv2.VideoWriter(fileName, cv2.VideoWriter_fourcc(vcodec[0], vcodec[1], vcodec[2], vcodec[3]), fps, (frameWidth, frameHeight), True)
    
    def write(self, image):
        """ Convert raw image format to something OpenCV understands """
        self.videoWriter.write(image)    
   
    def close(self):
        """Clean up resources"""
        self.videoWriter.release()
