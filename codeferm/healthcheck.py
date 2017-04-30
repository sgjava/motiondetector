"""
Created on Apr 23, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import os, threading, observer

class healthcheck(observer.observer):
    """Health check.
    
    Verify the health of videoloop. External process needs to monitor file mtime
    since file will not be updated if health check fails. Make sure the external
    process is aware of the file update interval set in fpsInterval.
    
    """
    
    def __init__(self, appConfig, logger):
        self.appConfig = appConfig
        self.logger = logger
        
    def check(self, frameBuf, fps, frameOk):
        """Verify videoloop health"""
        if len(frameBuf) <= fps * 2 and frameOk:
            self.logger.info("Health OK")
            fileName = os.path.expanduser(self.appConfig.healthFileName)
            fileDir = os.path.dirname(fileName)
            # Create dir if it doesn"t exist
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)
            # Write to health check file      
            with open(fileName, 'a') as f:
                f.write("OK")
        else:
            self.logger.info("Health not OK")
        
    def observeEvent(self, **kwargs):
        "Handle events"
        if kwargs["event"] == self.appConfig.healthCheck:
            # Kick off health check thread
            healthThread = threading.Thread(target=self.check, args=(kwargs["frameBuf"], kwargs["fps"], kwargs["frameOk"],))
            healthThread.start()
