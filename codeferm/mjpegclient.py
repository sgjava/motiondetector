"""
Created on Apr 12, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import socket, urlparse, base64, numpy, cv2

class mjpegclient(object):
    """MJPEG frame grabber class.
    
    Used for socket based frame grabber.

    """
    def __init__(self, url):
        # Parse URL
        parsed = urlparse.urlparse(url)
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
            token = base64.encodestring("%s:%s" % (parsed.username, parsed.password)).strip()
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
        self.socketFile = self.streamSock.makefile("rwb", bufsize=0)
        # Send HTTP GET for MJPEG stream
        self.socketFile.write("\r\n".join(lines) + "\r\n\r\n")
        # Read in HTTP headers
        self.line = self.socketFile.readline()
        while len(self.line) > 0 and self.line.strip() != "":
            parts = self.line.split(":")
            if len(parts) > 1 and parts[0].lower() == "content-type":
                # Extract boundary string from content-type
                content_type = parts[1].strip()
                self.boundary = content_type.split(";")[1].split("=")[1]
            self.line = self.socketFile.readline()
        # See if we found "content-type"
        if not self.boundary:
            raise Exception("Cannot find content-type")
        
    def getFrameLength(self):
        """Get frame length from stream"""
        self.line = self.socketFile.readline()
        # Find boundary
        while len(self.line) > 0 and self.line.count(self.boundary) == 0:
            self.line = self.socketFile.readline()
        # Read in chunk headers
        while len(self.line) > 0 and self.line.strip() != "":
            parts = self.line.split(":")
            if len(parts) > 1 and parts[0].lower().count("content-length") > 0:
                # Grab chunk length
                length = int(parts[1].strip())
            self.line = self.socketFile.readline()
        return length
    
    def getFrameRaw(self):
        """Get raw frame data from stream"""
        return self.socketFile.read(self.getFrameLength())
    
    def getFrame(self):
        """Get raw frame data from stream and decode"""
        jpeg = self.getFrameRaw()
        return jpeg, cv2.imdecode(numpy.fromstring(jpeg, numpy.uint8), cv2.IMREAD_COLOR)    
   
    def close(self):
        """Clean up resources"""
        self.socketFile.close()
        self.streamSock.close()
