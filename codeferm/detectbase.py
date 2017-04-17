"""
Created on Apr 16, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import abc, os, cv2, observable

class detectbase(observable.observable):
    """Detect abstract base class.
    
    Override detect function to do any image processing.

    """

    __metaclass__ = abc.ABCMeta

    def frameInfo(self, image, appConfig):
        """Set common frame info"""
        # Motion detection generally works best with 320 or wider images
        self.frameHeight, self.frameWidth, channels = image.shape
        self.widthDivisor = int(self.frameWidth / appConfig.resizeWidthDiv)
        if self.widthDivisor < 1:
            self.widthDivisor = 1
        self.frameResizeWidth = int(self.frameWidth / self.widthDivisor)
        self.frameResizeHeight = int(self.frameHeight / self.widthDivisor)
        # Used for full size image marking
        self.widthMultiplier = int(self.frameWidth / self.frameResizeWidth)
        self.heightMultiplier = int(self.frameHeight / self.frameResizeHeight)
        
    def saveFrame(self, image, saveDir, saveFileName):
        """Save frame"""
        # Create dir if it doesn"t exist
        if not os.path.exists(saveDir):
            os.makedirs(saveDir)
        cv2.imwrite("%s/%s" % (saveDir, saveFileName), image)        
        
    def inside(self, r, q):
        """See if one rectangle inside another"""
        rx, ry, rw, rh = r
        qx, qy, qw, qh = q
        return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh
    
    def markRectSize(self, image, rects, boxColor, boxThickness):
        """Mark rectangles in image"""
        for x, y, w, h in rects:
            # Calculate full size
            x2 = x * self.widthMultiplier
            y2 = y * self.heightMultiplier
            w2 = w * self.widthMultiplier
            h2 = h * self.heightMultiplier
            # Mark target
            cv2.rectangle(image, (x2, y2), (x2 + w2, y2 + h2), boxColor, boxThickness)
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
            cv2.putText(image, label, (x2, y2), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
