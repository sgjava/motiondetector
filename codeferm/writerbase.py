"""
Created on Dec 22, 2019

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import abc


class writerbase(object):
    """Frame writer abstract base class.
    
    Override functions to return numpy array that OpenCV can use. close()
    should do any cleanup required.

    """
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def write(self, image):
        """Encode frame from numpy array"""
        raise NotImplementedError("Please override in the derived class")
    
    @abc.abstractmethod
    def close(self):
        """Close connections, files, etc."""
        raise NotImplementedError("Please override in the derived class")
