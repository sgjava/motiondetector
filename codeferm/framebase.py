"""
Created on Feb 9, 2013

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import abc


class framebase(object):
    """Frame grabber abstract base class.
    
    Override functions to return numpy array that OpenCV can use. close()
    should do any cleanup required.

    """
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def getFrame(self):
        """Return frame as raw data"""
        raise NotImplementedError("Please override in the derived class")
    
    @abc.abstractmethod
    def decodeFrame(self, image):
        """Return frame as numpy array"""
        raise NotImplementedError("Please override in the derived class")
    
    @abc.abstractmethod
    def close(self):
        """Close connections, files, etc."""
        raise NotImplementedError("Please override in the derived class")
