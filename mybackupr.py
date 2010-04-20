#!/usr/bin/python

import flickrapi
import os
import downloader

API_KEY    = 'c03b993d9d80bbfec493172940e944a2'
API_SECRET = 'f557b4bdc67b58cc'

class MyBackupr:
    def main(self):
        self.flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET)

        self.homeDir   = os.path.expanduser('~')
        self.backupDir = self.homeDir + '/mybackupr'

        self.authenticate()
        self.backup()

    def backup(self):
        if not os.path.exists(self.backupDir):
            os.mkdir(self.backupDir, 0755)

        self.fetchPhotos()

        #result      = self.flickr.collections_getTree()
        #collections = result.find('collections').findall('collection')
        #path        = ['~', 'mybackupr']

        #self.fetchCollections(collections, path)

    def fetchPhotos(self, page=1):
        result = self.flickr.photos_search(user_id  = 'me',
                                           page     = page,
                                           per_page = 500,
                                           extras   = 'description,tags,url_o')

        photos = result.find('photos').findall('photo')

        for photo in photos:
            id          = photo.attrib['id']
            title       = photo.attrib['title']
            description = photo.find('description').text
            url         = photo.attrib['url_o']
            tags        = photo.attrib['tags']

            self.downloadPhoto(url, id);

    def downloadPhoto(self, url, id):
        print 'Downloading photo with ID: ' + id

        loader = downloader.Downloader(url, self.backupDir + '/' + id)
        loader.start()

    def fetchCollections(self, collections, path):
        for collection in collections:
            title = collection.attrib['title']

            path.append(collection.attrib['id'])

            sets           = collection.findall('set')
            subCollections = collection.findall('collection')

            if len(subCollections) > 0:
                self.fetchCollections(subCollections, path)

            if len(sets) > 0:
                self.fetchSets(sets, path)

            path.pop()

    def fetchSets(self, sets, path):
        for set in sets:
            path.append(set.attrib['id'])

            print '/'.join(path)

            path.pop()
    
    def authenticate(self):
        (token, frob) = self.flickr.get_token_part_one(perms='read')

        if not token:
            raw_input('Press ENTER after you authorized this program')

        self.flickr.get_token_part_two((token, frob))

if __name__ == '__main__':
    app = MyBackupr()
    app.main()
