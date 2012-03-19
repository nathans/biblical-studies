#! /usr/bin/env python
#
# Script to extract and rank all of Jesus words
# (c) 2012 Nathan Smith <nathan@smithfam.info>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
