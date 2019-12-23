"""
Created on Apr 12, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import socket, base64, numpy, cv2, framebase
from urllib.parse import urlparse


class mjpegclient(framebase.framebase):
    """MJPEG frame grabber class.
    
    Used for socket based frame grabber.

    """
    
    def __init__(self, url, timeout):
        """Connect to stream"""
        # Set socket timeout
        socket.setdefaulttimeout(timeout)        
        # Parse URL
        parsed = urlparse(url)
        port = parsed.port
        # Set port to default if not set
        if not port:
            port = 80
        # See if query string present
        if not parsed.query:
            path = parsed.path
        else:
            path = "%s%s%s" % (parsed.path, "?", parsed.query)   
        # See if we need to do HTTP basic access authentication
        if parsed.username is None:
            # Build HTTP header
            lines = [
                "GET %s HTTP/1.1" % path,
                "Host: %s" % parsed.hostname,
            ]
        else:
            # Base64 encode username and password
            token = base64.b64encode(("%s:%s" % (parsed.username, parsed.password)).encode('utf-8')).decode('utf-8')            
            # Build HTTP header
            lines = [
                "GET %s HTTP/1.1" % path,
                "Host: %s" % parsed.hostname,
                "Authorization: Basic %s" % token,
            ]
        # AF_INET: IPv4 protocols (both TCP and UDP)
        # SOCK_STREAM: a connection-oriented, TCP byte stream
        self.streamSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.streamSock.connect((parsed.hostname, port))
        # Socket file in read, write, binary mode and no buffer
        self.socketFile = self.streamSock.makefile("rwb", buffering=None)
        # Send HTTP GET for MJPEG stream
        self.socketFile.write("\r\n".join(lines).encode('utf-8') + b"\r\n\r\n")
        self.socketFile.flush()
        # Read in HTTP headers
        self.line = self.socketFile.readline()
        self.boundary = b""
        while len(self.line) > 0 and self.line.strip() != b"" and self.boundary == b"":
            if self.line.lower().find(b"content-type: multipart") >= 0:
                parts = self.line.split(b":")
                if len(parts) > 1 and parts[0].lower() == b"content-type":
                    # Extract boundary string from content-type
                    content_type = parts[1].strip()
                    self.boundary = content_type.split(b";")[1].split(b"=")[1]
            self.line = self.socketFile.readline()
        # See how many lines need to be skipped after 'content-length'
        while len(self.line) > 0 and self.line.strip().lower().find(b"content-length") < 0:
            self.line = self.socketFile.readline()
        # Find start of image
        self.skipLines = -1
        while len(self.line) > 0 and self.line.strip().lower().find(bytes.fromhex('ffd8')) != 0:
            self.line = self.socketFile.readline()
            self.skipLines += 1
        # Set basic params
        frame = self.getFrame()
        image = self.decodeFrame(frame)
        self.frameHeight, self.frameWidth, channels = image.shape
        self.fps = 0
        
    def getFrameLength(self):
        """Get frame length from stream"""
        self.line = self.socketFile.readline()
        # Find boundary
        while len(self.line) > 0 and self.line.count(self.boundary) == 0:
            self.line = self.socketFile.readline()
        length = 0
        # Read in chunk headers
        while len(self.line) > 0 and self.line.strip() != "" and length == 0:
            parts = self.line.split(b":")
            if len(parts) > 1 and parts[0].lower().count(b"content-length") > 0:
                # Grab chunk length
                length = int(parts[1].strip())
                # Skip lines before image data
                i = self.skipLines
                while i > 0:
                    self.line = self.socketFile.readline()
                    i -= 1                
            else:
                self.line = self.socketFile.readline()
        return length
    
    def getFrame(self):
        """Get raw frame data from stream"""
        return self.socketFile.read(self.getFrameLength())
    
    def decodeFrame(self, image):
        """ Convert raw image format to something OpenCV understands """
        return cv2.imdecode(numpy.fromstring(image, numpy.uint8), cv2.IMREAD_COLOR)    
   
    def close(self):
        """Clean up resources"""
        self.socketFile.close()
        self.streamSock.close()
