#!/usr/bin/env python
"""MyBackupr

This source file is subject to the new BSD license that is bundled
with this package in the file LICENSE.
"""
import thread

import os
import shutil
import flickrapi
import apiData
import Queue
from progressbar import ProgressBar, Percentage, Bar, ETA
from mybackupr.download import Download

class Sync:
    def __init__(self):
        self.flickr = flickrapi.FlickrAPI(apiData.API_KEY, apiData.API_SECRET)

        self.homeDir  = os.path.expanduser('~') + '/mybackupr'
        self.photoDir = self.homeDir + '/photos'
        self.folderDir = self.homeDir + '/folders'

        self.authenticate()

    def run(self):
        if not os.path.exists(self.homeDir):
            os.mkdir(self.homeDir, 0755)

        if not os.path.exists(self.photoDir):
            os.mkdir(self.photoDir, 0755)

        if os.path.exists(self.folderDir):
            shutil.rmtree(self.folderDir)

        os.mkdir(self.folderDir, 0755)

        self.fetchPhotos()

        print 'Syncing collections and sets...'

        result      = self.flickr.collections_getTree()
        collections = result.find('collections').findall('collection')
        path        = [self.homeDir, 'folders']
        self.sets   = []

        self.fetchCollections(collections, path)

        result  = self.flickr.photosets_getList()
        allSets = result.find('photosets').findall('photoset')
        sets    = []

        for set in allSets:
            if not set.attrib['id'] in self.sets:
                sets.append(set)
            
        self.fetchSets(sets, path)

    def fetchPhotos(self, page=1):
        result = self.flickr.photos_search(user_id  = 'me',
                                           page     = page,
                                           per_page = 500,
                                           extras   = 'description,tags,url_o')

        root   = result.find('photos')
        photos = root.findall('photo')

        if page == 1:
            print 'Syncing ' + root.attrib['total'] + ' photos...'

            self.queue       = Queue.Queue()
            self.progressBar = ProgressBar(int(root.attrib['total']), [Percentage(), ' ', Bar(), ' ', ETA()]).start()
            self.threads = []

            for i in range(5):
                thread = Download(self.queue, self.progressBar)
                thread.daemon = True
                thread.start()
                self.threads.append(thread)

        for photo in photos:
            id          = photo.attrib['id']
            title       = photo.attrib['title']
            description = photo.find('description').text
            url         = photo.attrib['url_o']
            tags        = photo.attrib['tags']

            path = self.photoDir + '/' + id + '.jpg'

            if not os.path.exists(path):
                self.queue.put((url, path))
            else:
                self.progressBar.update(self.progressBar.currval + 1)

        if root.attrib['pages'] < page:
            self.fetchPhotos(page + 1)
        else:
            self.queue.join()
            self.progressBar.finish()

            for thread in self.threads:
                thread.kill()

            self.queue   = None
            self.threads = None

            print 'Sync complete'

    def fetchCollections(self, collections, path):
        for collection in collections:
            path.append(collection.attrib['title'])

            if not os.path.exists('/'.join(path)):
                os.mkdir('/'.join(path), 0755)

            sets           = collection.findall('set')
            subCollections = collection.findall('collection')

            if len(subCollections) > 0:
                self.fetchCollections(subCollections, path)

            if len(sets) > 0:
                self.fetchSets(sets, path)

            path.pop()

    def fetchSets(self, sets, path):
        for set in sets:
            path.append(set.attrib['title'])

            if not os.path.exists('/'.join(path)):
                os.mkdir('/'.join(path), 0755)

            for photo in self.flickr.walk_set(set.attrib['id']):
                os.symlink(self.photoDir + '/' + photo.attrib['id'] + '.jpg', '/'.join(path) + '/' + photo.attrib['id'] + '.jpg')

            path.pop()

            self.sets.append(set.attrib['id'])

    def authenticate(self):
        (token, frob) = self.flickr.get_token_part_one(perms='read')

        if not token:
            raw_input('Press ENTER after you authorized this program')

        self.flickr.get_token_part_two((token, frob))
