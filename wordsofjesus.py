#! /usr/bin/env python
#
# Script to extract and rank all of Jesus words
# (c) 2012 Nathan Smith <nathan@smithfam.info>

import os
import StringIO
import urllib
import xml.sax
import zipfile

import nltk
from nltk.corpus import stopwords

stops = stopwords.words('english')
url = 'http://ebible.org/web/eng-web_usfx.zip'

class WEBParser(xml.sax.handler.ContentHandler):
    """Class to parse WEB XML and extract words of Jesus"""

    def __init__(self):
        self.in_wj = False
        self.words = ""

    def startElement(self,name, attrs):
        if name == "wj":
            self.in_wj = True

    def characters(self, data):
        if self.in_wj:
            self.words += data.lower()

    def endElement(self, name):
        if name == "wj":
            self.in_wj = False

if __name__ == '__main__':
    if not os.path.exists(os.path.basename(url)):
        try:
            urllib.urlretrieve(url, os.path.basename(url))
        except:
            sys.exit(1)

    web_zip = os.path.basename(url)
    parser = xml.sax.make_parser()
    web = WEBParser()
    parser.setContentHandler(web)
    _zip = zipfile.ZipFile(web_zip)
    parser.parse(StringIO.StringIO(_zip.read("eng-web_usfx.xml")))
    words_of_jesus = nltk.word_tokenize(web.words)
    word_list = [w for w in words_of_jesus if (w not in stops and w.isalpha())]
    fdist = nltk.FreqDist(word_list)
    for word, count in fdist.items()[:100]:
        print "%s - %d" % (word, count)
