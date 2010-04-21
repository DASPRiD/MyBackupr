#!/usr/bin/env python
"""MyBackupr

This source file is subject to the new BSD license that is bundled
with this package in the file LICENSE.
"""

from urllib2 import Request, urlopen, URLError, HTTPError
from threading import Thread
from Queue import Empty

class Download(Thread):
    def __init__(self, queue, progressBar):
        Thread.__init__(self)

        self.queue       = queue
        self.progressBar = progressBar
        self.killed      = False

    def run(self):
        while not self.killed:
            try:
                (url, path) = self.queue.get(True, 1)
            except Empty, e:
                continue
            
            request = Request(url)

            try:
                source = urlopen(request)
                target = open(path, 'w')

                target.write(source.read())
                target.close
                source.close()
            except HTTPError, e:
                print 'HTTP Error: ', e.code , url
            except URLError, e:
                print 'URL Error: ', e.reason , url

            self.queue.task_done()
            self.progressBar.update(self.progressBar.currval + 1)

    def kill(self):
        self.killed = True
