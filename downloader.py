#!/usr/bin/python

from urllib2 import Request, urlopen, URLError, HTTPError
from threading import Thread

class Downloader(Thread):
    def __init__(self, url, target):
        Thread.__init__(self)

        self.url    = url
        self.target = target

    def run(self):
        request = Request(self.url)

        try:
            source = urlopen(request)
            target = open(self.target, 'w')

            target.write(source.read())
            target.close
            source.close()
        except HTTPError, e:
            print 'HTTP Error: ', e.code , url
	except URLError, e:
            print 'URL Error: ', e.reason , url
        
