"""
Created on Apr 12, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import subprocess, numpy, ffmpeg, writerbase


class ffmpegwriter(writerbase.writerbase):
    """Video writer based on ffmpeg-python.
    
    Encode single numpy image as video frame.

    """
    
    def __init__(self, fileName, vcodec, fps, frameWidth, frameHeight):
        self.process = self.startProcess(fileName, vcodec, fps, frameWidth, frameHeight)
        
    def startProcess(self, fileName, vcodec, fps, frameWidth, frameHeight):
        args = (
            ffmpeg
            .input('pipe:', framerate='{}'.format(fps), format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(frameWidth, frameHeight), loglevel='error')
            .output(fileName, vcodec=vcodec, pix_fmt='nv21', **{'b:v': 2000000})
            .overwrite_output()
            .compile()
        )
        return subprocess.Popen(args, stdin=subprocess.PIPE)        
    
    def write(self, image):
        """ Convert raw image format to something ffmpeg understands """
        self.process.stdin.write(
            image
            .astype(numpy.uint8)
            .tobytes()
        )        
   
    def close(self):
        """Clean up resources"""
        self.process.stdin.close()
        self.process.wait()
