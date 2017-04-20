"""
Created on Apr 12, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import os, subprocess, threading, observer

class scpfiles(observer.observer):
    """SCP files in subprocess.
    
    """
    
    def __init__(self, appConfig, logger):
        self.appConfig = appConfig
        self.logger = logger
        self.curRemoteDir = ""
    
    def copyFile(self, logger, hostName, userName, localFileName, remoteDir, deleteSource, timeout):
        """SCP file using command line."""
        # Create remote dir only once
        if self.curRemoteDir != remoteDir:
            self.curRemoteDir = remoteDir
            # Give mkdir time to work
            beforeScp = "sleep 2; "
            # mkdir on remote host
            command = "ssh %s@%s \"%s\"" % (userName, hostName, "mkdir -p %s" % remoteDir)
            logger.info(" Submitting %s" % command)
            proc = subprocess.Popen([command], shell=True)
            logger.info("Submitted process %d" % proc.pid)
        else:
            beforeScp = ""
        # scp file
        if deleteSource:
            deleteCommand = "; rm -f %s" % localFileName
        else:
            deleteCommand = ""
        command = "%sscp %s %s@%s:%s/%s%s" % (beforeScp, localFileName, userName, hostName, remoteDir, os.path.basename(localFileName), deleteCommand)
        logger.info(" Submitting %s" % command)
        proc = subprocess.Popen([command], shell=True)
        logger.info("Submitted process %d" % proc.pid)
        
    def observeEvent(self, **kwargs):
        "Handle events"
        if kwargs["event"] == self.appConfig.stopRecording:
            # Kick off startRecording thread
            scpThread = threading.Thread(target=self.copyFile, args=(self.logger, self.appConfig.hostName, self.appConfig.userName, kwargs["videoFileName"], os.path.expanduser(self.appConfig.remoteDir), self.appConfig.deleteSource, self.appConfig.timeout,))
            scpThread.start()
       
