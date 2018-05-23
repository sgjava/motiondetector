"""
Created on Apr 12, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import configparser, cv2


class config(object):
    """Configuration class.
    
    This makes it easy to pass around app configuration.

    """
    
    # Event type attributes
    motionStart, motionStop, pedestrianDetected, cascadeDetected, circleDetected, recordingStart, recordingStop, healthCheck = range(0, 8)    

    def __init__(self, fileName):
        """ Read configuration from INI file """
        parser = configparser.SafeConfigParser()
        # Read configuration file
        parser.read(fileName)
        # Logging related attributes
        self.logging = {'level' : parser.get("logging", "level"),
                        'formatter' : parser.get("logging", "formatter")}
        # Set camera related data attributes
        self.camera = {'name' :  parser.get("camera", "name"),
                       'framePlugin' :  parser.get("camera", "framePlugin"),
                       'videoCaptureProperties' :  eval(parser.get("camera", "videoCaptureProperties")),
                       'videoloopPlugins' :  eval(parser.get("camera", "videoloopPlugins"), {}, {}),
                       'url' :  parser.get("camera", "url"),
                       'socketTimeout' :  parser.getint("camera", "socketTimeout"),
                       'resizeWidthDiv' :  parser.getint("camera", "resizeWidthDiv"),
                       'detectPlugin' :  parser.get("camera", "detectPlugin"),
                       'fpsInterval' :  parser.getfloat("camera", "fpsInterval"),
                       'fps' :  parser.getint("camera", "fps"),
                       'frameBufMax' :  parser.getint("camera", "frameBufMax"),
                       'fourcc' :  parser.get("camera", "fourcc"),
                       'recordFileExt' :  parser.get("camera", "recordFileExt"),
                       'recordDir' :  parser.get("camera", "recordDir"),
                       'mark' :  parser.getboolean("camera", "mark"),
                       'saveFrames' :  parser.getboolean("camera", "saveFrames")}
        # Set motion related data attributes
        self.motion = {'ignoreMask' : parser.get("motion", "ignoreMask"),
                       'kSize' : eval(parser.get("motion", "kSize"), {}, {}),
                       'alpha' : parser.getfloat("motion", "alpha"),
                       'blackThreshold' : parser.getint("motion", "blackThreshold"),
                       'maxChange' : parser.getfloat("motion", "maxChange"),
                       'startThreshold' : parser.getfloat("motion", "startThreshold"),
                       'stopThreshold' : parser.getfloat("motion", "stopThreshold"),
                       'historyImage' : parser.getboolean("motion", "historyImage"),
                       # Set contour related data attributes
                       'dilateAmount' : parser.getint("motion", "dilateAmount"),
                       'erodeAmount' : parser.getint("motion", "erodeAmount")}
        # Set pedestrian detect related data attributes
        self.pedestrian = {'hitThreshold' : parser.getfloat("pedestrian", "hitThreshold"),
                           'winStride' : eval(parser.get("pedestrian", "winStride"), {}, {}),
                           'padding' : eval(parser.get("pedestrian", "padding"), {}, {}),
                           'scale0' : parser.getfloat("pedestrian", "scale0"),
                           'minHogWeight' : parser.getfloat("pedestrian", "minHogWeight"),
                           'detectorFile' : parser.get("pedestrian", "detectorFile")}
        # Set cascade related data attributes
        self.cascade = {'cascadeFile' : parser.get("cascade", "cascadeFile"),
                        'scaleFactor' : parser.getfloat("cascade", "scaleFactor"),
                        'minNeighbors' : parser.getint("cascade", "minNeighbors"),
                        'minWidth' : parser.getint("cascade", "minWidth"),
                        'minHeight' : parser.getint("cascade", "minHeight"),
                        'minCascadeWeight' : parser.getint("cascade", "minCascadeWeight")}
        # Set Hough Circles related attributes
        self.hough = {'methodType' : int(eval(parser.get("hough", "methodType"))),
                      'dp': parser.getint("hough", "dp"),
                      'minDist': parser.getint("hough", "minDist"),
                      'param1': parser.getint("hough", "param1"),
                      'param2': parser.getint("hough", "param2"),
                      'minRadius': parser.getint("hough", "minRadius"),
                      'maxRadius': parser.getint("hough", "maxRadius")}
        # Set SCP related attributes
        self.scp = {'hostName' : parser.get("scp", "hostName"),
                    'userName' : parser.get("scp", "userName"),
                    'remoteDir' : parser.get("scp", "remoteDir"),
                    'timeout' : parser.getint("scp", "timeout"),
                    'deleteSource' : parser.getboolean("scp", "deleteSource")}        
        # Set health check related attributes
        self.health = {'fileName' : parser.get("health", "fileName"),
                    'mqttHost' : parser.get("health", "mqttHost"),
                    'mqttPort' : parser.getint("health", "mqttPort"),
                    'mqttTopic' : parser.get("health", "mqttTopic")}        
                    
