"""
Created on Nov 22, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import threading, observer


class healthcheckmqtt(observer.observer):
    """Health check.
    
    Verify the health of videoloop. External process needs to monitor MQTT topic.
    Based on PR from Joao Paulo Barraca.
    
    """
    
    def __init__(self, appConfig, logger):
        self.appConfig = appConfig
        self.logger = logger
        self.mqttc = None
        # Initilize MQTT if host set
        if self.appConfig.health['mqttHost']:
            try:
                self.logger.info("Enabling Health MQTT to %s:%d" % (self.appConfig.health['mqttHost'], self.appConfig.health['mqttPort']))
                import paho.mqtt.client as mqtt
                self.mqttc = mqtt.Client()
                self.mqttc.connect(self.appConfig.health['mqttHost'], self.appConfig.health['mqttPort'], 60)
                mqttThread = threading.Thread(target=self.mqttLoop)
                mqttThread.daemon = True
                mqttThread.start()
            except Exception, e:
                self.logger.exception("Could not connect to MQTT Broker. MQTT Disabled")
                self.mqttEnabled = False        
        
    def check(self, frameBuf, fps, frameOk):
        """Verify videoloop health"""
        if len(frameBuf) <= fps * 2 and frameOk:
            self.logger.info("Health OK")
            self.mqttSend("OK")
        else:
            self.logger.info("Health not OK")
            self.mqttSend("NOT OK")

    def mqttSend(self, message):
        if self.mqttc is not None:
            self.mqttc.publish(self.appConfig.health['mqttTopic'], message)            

    def mqttLoop(self):
        self.mqttc.loop_forever()
        
    def observeEvent(self, **kwargs):
        "Handle events"
        if kwargs["event"] == self.appConfig.healthCheck:
            # Kick off health check thread
            healthThread = threading.Thread(target=self.check, args=(kwargs["frameBuf"], kwargs["fps"], kwargs["frameOk"],))
            healthThread.start()
