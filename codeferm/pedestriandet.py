"""
Created on Apr 16, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import cv2, detectbase


class pedestriandet(detectbase.detectbase):
    """Pedestrian detector using ROI.
    
    Histogram of Oriented Gradients ([Dalal2005]) object detector is used.
    
    """
    
    def __init__(self, appConfig, image, logger):
        """Init object"""
        self.appConfig = appConfig
        # Set frame information
        self.frameInfo(image, appConfig)
        # Initialize HOG
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.pedestrianDetected = False
        self.logger = logger

    def filterByWeight(self, foundLocsList, foundWghtsList, minWeight):
        """Filter out found locations by weight"""
        filteredFoundLocations = []
        filteredFoundWeights = []
        for foundWeights, foundLocations in zip(foundWghtsList, foundLocsList):
            filteredLocations = []
            filteredWeights = []
            i = 0
            # Filter by weight
            for w in foundWeights:
                if w >= minWeight:
                    filteredLocations.append(foundLocations[i])
                    filteredWeights.append(w)
                i += 1
            if len(filteredLocations) > 0:
                filteredFoundLocations.append(filteredLocations)
                filteredFoundWeights.append(filteredWeights)
        return filteredFoundLocations, filteredFoundWeights
    
    def detect(self, image, resizeImg, grayImg, timestamp, locations):
        """Check ROI for pedestrians"""
        locationsList = []
        foundLocationsList = []
        foundWeightsList = []
        for x, y, w, h in locations:
            # Make sure ROI is big enough for detector
            if w > 63 and h > 127:
                imageRoi = resizeImg[y:y + h, x:x + w]
                foundLocations, foundWeights = self.hog.detectMultiScale(imageRoi, winStride=self.appConfig.winStride, padding=self.appConfig.padding, scale=self.appConfig.scale0)
                if len(foundLocations) > 0:
                    locationsList.append((x, y, w, h))
                    foundLocationsList.append(foundLocations)
                    foundWeightsList.append(foundWeights)
        # Any hits?
        if len(foundLocationsList) > 0:
            # Only filter if minWeight > 0.0
            if self.appConfig.minHogWeight > 0.0:
                # Filter found location by weight
                foundLocationsList, foundWeightsList = self.filterByWeight(foundLocationsList, foundWeightsList, self.appConfig.minHogWeight)
            # Any hits after possible filtering?
            if len(foundLocationsList) > 0:
                self.pedestrianDetected = True
                if self.appConfig.mark:
                    # Draw rectangle around found objects
                    self.markRectWeight(image, locationsList, foundLocationsList, foundWeightsList, (255, 0, 0), 2)
                # self.logger.debug("Pedestrian detected locations: %s" % foundLocationsList)
                # Let listening objects know pedestrian detected      
                self.notifyObservers(event=self.appConfig.pedestrianDetected, timestamp=timestamp)
        return locationsList, foundLocationsList, foundWeightsList
    
    def markRectWeight(self, image, locList, foundLocsList, foundWghtsList, boxColor, boxThickness):
        """Mark ROI rectangles with weight in image"""
        for location, foundLocations, foundWeights in zip(locList, foundLocsList, foundWghtsList):
            i = 0
            # Mark target
            for x, y, w, h in foundLocations:
                # Calculate full size
                x2 = x * self.widthMultiplier
                y2 = y * self.heightMultiplier
                w2 = w * self.widthMultiplier
                h2 = h * self.heightMultiplier
                x3, y3, w3, h3 = location
                # Calculate full size
                x4 = x3 * self.widthMultiplier
                y4 = y3 * self.heightMultiplier
                # Mark target
                cv2.rectangle(image, (x2 + x4, y2 + y4), (x2 + x4 + w2, y2 + y4 + h2), boxColor, boxThickness)
                label = "%1.2f" % foundWeights[i]
                # Figure out text size
                size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1.0, 1)[0]            
                # Print weight
                cv2.putText(image, label, (x2 + x4, y2 + y4 + h2 - size[1]), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
                i += 1
