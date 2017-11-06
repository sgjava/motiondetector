"""
Created on Apr 14, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""


class observable(list):
    """A class of thing that can be observed.
    
    When its notifyObservers() method is called with an event, it passes that
    event on to its observers as a dictionary.
    
    """

    def addObserver(self, observer):
        self.append(observer)

    def notifyObservers(self, **kwargs):
        for observer in self:
            observer.observeEvent(**kwargs)
