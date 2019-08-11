"""
Created on Apr 14, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import os, cv2, numpy, detectbase


class motiondet(detectbase.detectbase):
    """Motion detection image processor.
    
    Uses moving average to determine change percent.
    
    """
    
    def __init__(self, appConfig, image, logger):
        """Init object"""
        self.appConfig = appConfig
        # Read ignore mask image if set
        if appConfig.motion['ignoreMask'] != "":
            self.maskImg = cv2.imread(os.path.expanduser(appConfig.motion['ignoreMask']), 0)
            logger.info("Using ignore mask: %s" % appConfig.motion['ignoreMask'])            
        else:
            self.maskImg = None   
        self.movingAvgImg = None
        # Set frame information
        self.frameInfo(image, appConfig)
        logger.info("Image resized to: %dx%d" % (self.frameResizeWidth, self.frameResizeHeight))
        self.motionDetected = False
        self.logger = logger

    def contours(self, image):
        """Return contours"""
        # The background (bright) dilates around the black regions of frame
        image = cv2.dilate(image, None, iterations=self.appConfig.motion['dilateAmount'])
        # The bright areas of the image (the background, apparently), get thinner, whereas the dark zones bigger
        image = cv2.erode(image, None, iterations=self.appConfig.motion['erodeAmount']);
        # Find contours
        contours, heirarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
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
        workImg = cv2.blur(resizeImg, self.appConfig.motion['kSize'])
        # Generate moving average image if needed
        if self.movingAvgImg is None:
            self.movingAvgImg = numpy.float32(workImg)
        # Generate moving average image
        cv2.accumulateWeighted(workImg, self.movingAvgImg, self.appConfig.motion['alpha'])
        diffImg = cv2.absdiff(workImg, cv2.convertScaleAbs(self.movingAvgImg))
        # Convert to grayscale
        grayImg = cv2.cvtColor(diffImg, cv2.COLOR_BGR2GRAY)
        # Convert to BW
        ret, bwImg = cv2.threshold(grayImg, self.appConfig.motion['blackThreshold'], 255, cv2.THRESH_BINARY)
        # Apply ignore mask
        if self.maskImg is None:
            motionImg = bwImg
        else:
            motionImg = numpy.bitwise_and(bwImg, self.maskImg)     
        # Total number of changed motion pixels
        height, width, channels = resizeImg.shape
        motionPercent = 100.0 * cv2.countNonZero(motionImg) / (width * height)
        # Detect if camera is adjusting and reset reference if more than threshold
        if motionPercent > self.appConfig.motion['maxChange']:
            self.movingAvgImg = numpy.float32(workImg)
            self.logger.info("%4.2f%% motion greater than maximum of %4.2f%%, image reset" % (motionPercent, self.appConfig.motion['maxChange']))
        # Analyze entire image even if ignore mask used, otherwise the ROI could be partially truncated
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
                if regPercent < self.appConfig.motion['maxChange'] :
                    movementLocationsFiltered.append(r)
        if self.appConfig.camera['mark']:
            # Draw rectangle around found objects
            self.markRectSize(image, movementLocationsFiltered, (0, 255, 0), 2)
        # Motion start stop events
        if self.motionDetected:
            if motionPercent <= self.appConfig.motion['stopThreshold']:
                self.motionDetected = False
                # Let listening objects know motion has stopped      
                self.notifyObservers(event=self.appConfig.motionStop, motionPercent=motionPercent, timestamp=timestamp)
        # Threshold to trigger motionStart
        elif motionPercent > self.appConfig.motion['startThreshold'] and motionPercent < self.appConfig.motion['maxChange']:
            self.motionDetected = True
            # Let listening objects know motion has started      
            self.notifyObservers(event=self.appConfig.motionStart, motionPercent=motionPercent, timestamp=timestamp)
        return resizeImg, grayImg, bwImg, motionPercent, movementLocationsFiltered
