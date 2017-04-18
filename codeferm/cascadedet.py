"""
Created on Apr 17, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import os, cv2, detectbase

class cascadedet(detectbase.detectbase):
    """Cascade classifier detector using ROI.
    
    """
    
    def __init__(self, appConfig, image, logger):
        """Init object"""
        self.appConfig = appConfig
        # Set frame information
        self.frameInfo(image, appConfig)
        # Initialize classifier
        self.cascade = cv2.CascadeClassifier(os.path.expanduser(appConfig.cascadeFile))
        self.cascadeDetected = False
        self.logger = logger

    def filterByWeight(self, foundLocsList):
        """Filter out found locations by weight"""
        filteredFoundLocations = []
        filteredFoundWeights = []
        # Process all ROIs
        for locList in foundLocsList:
            locations = []
            weight = 0
            # Filter out inside rectangles
            for ri, r in enumerate(locList):
                for qi, q in enumerate(locList):
                    if ri != qi and self.inside(r, q):
                        weight += 1
                        break
                else:
                    rx, ry, rw, rh = r
                    locations.append(r)
            # Filter out by weight
            if weight >= self.appConfig.minCascadeWeight:
                filteredFoundLocations.append(locations)
                filteredFoundWeights.append(weight)
        return filteredFoundLocations, filteredFoundWeights
    
    def detect(self, image, timestamp, locations):
        """Cascade detect ROI"""
        locationsList = []
        foundLocationsList = []
        foundWeightsList = []
        for x, y, w, h in locations:
            # Make sure ROI is big enough for detector
            if w > self.appConfig.minWidth and h > self.appConfig.minHeight:
                # Image should be gray scale
                imageRoi = image[y:y + h, x:x + w]
                foundLocations = self.cascade.detectMultiScale(imageRoi, self.appConfig.scaleFactor, self.appConfig.minNeighbors)
                if len(foundLocations) > 0:
                    locationsList.append((x, y, w, h))
                    foundLocationsList.append(foundLocations)
        if len(foundLocationsList) > 0:
            foundLocationsList, foundWeightsList = self.filterByWeight(foundLocationsList)
            if len(foundLocationsList) > 0:
                self.cascadeDetected = True
                if self.appConfig.mark:
                    # Draw rectangle around found objects
                    self.markRoi(image, locationsList, foundLocationsList, (255, 0, 0), 2)
                                # Let listening objects know pedestrian detected      
                    self.notifyObservers(event=self.appConfig.cascadeDetected, timestamp=timestamp)
                #self.logger.debug("Cascade detected locations: %s, weights: %s" % (foundLocationsList, foundWeightsList))
        return locationsList, foundLocationsList, foundWeightsList
    
    def markRoi(self, image, locList, foundLocsList, boxColor, boxThickness):
        """Mark ROI objects in image"""
        for location, foundLocations in zip(locList, foundLocsList):
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
                label = "%dx%d" % (w2, h2)
                # Figure out text size
                size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1.0, 1)[0]            
                # Deal with possible text outside of image bounds
                if x2 < 0:
                    x2 = 0
                if y2 < size[1]:
                    y2 = size[1] + 2
                else:
                    y2 = y2 - 2
                # Show width and height of full size image
                cv2.putText(image, label, (x2 + x4, y2 + y4), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
