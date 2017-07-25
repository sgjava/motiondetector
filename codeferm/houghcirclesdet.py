"""
Created on Jul 24, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import cv2, numpy, detectbase


class houghcirclesdet(detectbase.detectbase):
    """Hough Circles detector using ROI.
    
    Hough Gradient Method.
    
    """
    
    def __init__(self, appConfig, image, logger):
        """Init object"""
        self.appConfig = appConfig
        # Set frame information
        self.frameInfo(image, appConfig)
        self.circleDetected = False
        self.logger = logger
    
    def detect(self, image, resizeImg, grayImg, timestamp, locations):
        """Check ROI for circles"""
        locationsList = []
        foundLocations = []
        foundLocationsList = []
        foundWeightsList = []
        for x, y, w, h in locations:
            imageRoi = grayImg[y:y + h, x:x + w]
            #circles = cv2.HoughCircles(imageRoi, self.appConfig.methodType, self.appConfig.dp, self.appConfig.minDist, self.appConfig.param1, self.appConfig.param2, self.appConfig.minRadius, self.appConfig.maxRadius)
            circles = cv2.HoughCircles(imageRoi,cv2.HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=0,maxRadius=0)
            if circles is not None:
                circles = numpy.uint16(numpy.around(circles))      
                for i in circles[0,:]:
                    foundLocations.append((i[0], i[1], i[2]))
                if len(foundLocations) > 0:
                    locationsList.append((x, y, w, h))
                    foundLocationsList.append(foundLocations)
        # Any hits?
        if len(foundLocationsList) > 0:
            self.circleDetected = True
            if self.appConfig.mark:
                # Draw rectangle around found objects
                self.markCircle(image, locationsList, foundLocationsList, (255, 0, 0), 2)
            # self.logger.debug("Circle detected locations: %s" % foundLocationsList)
            # Let listening objects know circle detected      
            self.notifyObservers(event=self.appConfig.circleDetected, timestamp=timestamp)
        return locationsList, foundLocationsList, foundWeightsList
    
    def markCircle(self, image, locList, foundLocsList, boxColor, boxThickness):
        """Mark ROI circles"""
        for location, foundLocations in zip(locList, foundLocsList):
            i = 0
            # Mark target
            for x, y, r in foundLocations:
                # Calculate full size
                x2 = x * self.widthMultiplier
                y2 = y * self.heightMultiplier
                r2 = r * self.widthMultiplier
                x3, y3, w3, h3 = location
                # Calculate full size
                x4 = x3 * self.widthMultiplier
                y4 = y3 * self.heightMultiplier
                # Mark target
                cv2.circle(image, (x2 + x4, y2 + y4), r2, boxColor, boxThickness)
