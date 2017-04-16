"""
Created on Apr 14, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import cv2, numpy, observable

class motiondet(observable.observable):
    """Motion detection image processor.
    
    Uses moving average to determine change percent.
    
    """
    
    # Event types class attributes
    motionStart, motionStop = range(0, 2)
    
    def __init__(self, appConfig, image, logger):
        """Init object"""
        self.appConfig = appConfig
        # Read ignore mask image if set
        if appConfig.ignoreMask != "":
            self.maskImg = cv2.imread(appConfig.ignoreMask, 0)
            logger.info("Using ignore mask: %s" % appConfig.ignoreMask)            
        else:
            self.maskImg = None   
        self.movingAvgImg = None
        # Motion detection generally works best with 320 or wider images
        self.frameHeight, self.frameWidth, channels = image.shape
        self.widthDivisor = int(self.frameWidth / appConfig.resizeWidthDiv)
        if self.widthDivisor < 1:
            self.widthDivisor = 1
        self.frameResizeWidth = int(self.frameWidth / self.widthDivisor)
        self.frameResizeHeight = int(self.frameHeight / self.widthDivisor)
        logger.info("Resized to: %dx%d" % (self.frameResizeWidth, self.frameResizeHeight))
        self.motionDetected = False
        self.logger = logger

    def inside(self, r, q):
        """See if one rectangle inside another"""
        rx, ry, rw, rh = r
        qx, qy, qw, qh = q
        return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh
    
    def contours(self, image):
        """Return contours"""
        # The background (bright) dilates around the black regions of frame
        image = cv2.dilate(image, None, iterations=self.appConfig.dilateAmount);
        # The bright areas of the image (the background, apparently), get thinner, whereas the dark zones bigger
        image = cv2.erode(image, None, iterations=self.appConfig.erodeAmount);
        # Find contours
        image, contours, heirarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Add objects with motion
        movementLocations = []
        for contour in contours:
            rect = cv2.boundingRect(contour)
            movementLocations.append(rect)
        return movementLocations
    
    def detect(self, image, timestamp):
        """Detect motion"""
        # Resize image if not the same size as the original
        if self.frameResizeWidth != self.frameWidth:
            resizeImg = cv2.resize(image, (self.frameResizeWidth, self.frameResizeHeight), interpolation=cv2.INTER_NEAREST)
        else:
            resizeImg = image
        movementLocationsFiltered = []
        # Generate work image by blurring
        workImg = cv2.blur(resizeImg, self.appConfig.kSize)
        # Generate moving average image if needed
        if self.movingAvgImg is None:
            self.movingAvgImg = numpy.float32(workImg)
        # Generate moving average image
        cv2.accumulateWeighted(workImg, self.movingAvgImg, self.appConfig.alpha)
        diffImg = cv2.absdiff(workImg, cv2.convertScaleAbs(self.movingAvgImg))
        # Convert to grayscale
        grayImg = cv2.cvtColor(diffImg, cv2.COLOR_BGR2GRAY)
        # Convert to BW
        ret, bwImg = cv2.threshold(grayImg, self.appConfig.blackThreshold, 255, cv2.THRESH_BINARY)
        # Apply ignore mask
        if self.maskImg is not None:
            bwImg = numpy.bitwise_and(bwImg, self.maskImg)     
        # Total number of changed motion pixels
        height, width, channels = resizeImg.shape
        motionPercent = 100.0 * cv2.countNonZero(bwImg) / (width * height)
        # Detect if camera is adjusting and reset reference if more than threshold
        if motionPercent > self.appConfig.maxChange:
            self.movingAvgImg = numpy.float32(workImg)
        movementLocations = self.contours(bwImg)
        # Filter out inside rectangles
        for ri, r in enumerate(movementLocations):
            for qi, q in enumerate(movementLocations):
                if ri != qi and self.inside(r, q):
                    break
            else:
                rx, ry, rw, rh = r
                regPercent = ((rw * rh) / (width * height)) * 100.0
                # Toss rectangles >= maxChange percent of total frame
                if regPercent < self.appConfig.maxChange :
                    movementLocationsFiltered.append(r)
        # Motion start stop events
        if self.motionDetected:
            if motionPercent <= self.appConfig.stopThreshold:
                self.motionDetected = False
                # Let listening objects know motion has stopped      
                self.notifyObservers(event=motiondet.motionStop, motionPercent=motionPercent, timestamp=timestamp)
        # Threshold to trigger motionStart
        elif motionPercent > self.appConfig.startThreshold:
            self.motionDetected = True
            # Let listening objects know motion has started      
            self.notifyObservers(event=motiondet.motionStart, motionPercent=motionPercent, timestamp=timestamp)
        return resizeImg, grayImg, bwImg, motionPercent, movementLocationsFiltered
