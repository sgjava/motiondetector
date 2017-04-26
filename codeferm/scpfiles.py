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
    
    def copyFile(self, hostName, userName, localFileName, remoteDir, deleteSource, timeout):
        """SCP file using command line."""
        command = ""
        # Get date part of local path and add to remote dir
        remoteDir += "/" + os.path.split(os.path.split(localFileName)[0])[1]
        # Create remote dir only once
        if self.curRemoteDir != remoteDir:
            self.curRemoteDir = remoteDir
            # mkdir on remote host
            command += "ssh %s@%s \"%s\"; " % (userName, hostName, "mkdir -p %s" % remoteDir)
        # Copy images dir if it exists
        imagesPath = os.path.splitext(localFileName)[0]
        if os.path.exists(imagesPath):
            command += "scp -r %s %s@%s:%s; " % (imagesPath, userName, hostName, remoteDir)
        # Copy history image
        if self.appConfig.historyImage:
            command += "scp %s.png %s@%s:%s/%s.png; " % (localFileName, userName, hostName, remoteDir, os.path.basename(localFileName))
        # Copy video file    
        command += "scp %s %s@%s:%s/%s" % (localFileName, userName, hostName, remoteDir, os.path.basename(localFileName))
        # Delete source files after SCP?
        if deleteSource:
            command += "; rm -f %s %s.png; rm -rf %s " % (localFileName, localFileName, imagesPath)
        self.logger.info(" Submitting %s" % command)
        proc = subprocess.Popen([command], shell=True)
        self.logger.info("Submitted process %d" % proc.pid)
        
    def observeEvent(self, **kwargs):
        "Handle events"
        if kwargs["event"] == self.appConfig.stopRecording:
            # Kick off scp thread
            scpThread = threading.Thread(target=self.copyFile, args=(self.appConfig.hostName, self.appConfig.userName, kwargs["videoFileName"], os.path.expanduser(self.appConfig.remoteDir), self.appConfig.deleteSource, self.appConfig.timeout,))
            scpThread.start()
