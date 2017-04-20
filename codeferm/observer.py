"""
Created on Apr 14, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

class observer(object):
    """A class of thing that observes an Observable.
    
    The Observable will call the Observer"s observeEvent() method.
    
    """

    def observeEvent(self, **kwargs):
        raise NotImplementedError, "Please override in the derived class"
