# sblgnt.py
# Imports the SBLGNT from plain text and loads it into an NLTK corpus
# (c) 2013 Nathan Smith <nathan@smithfam.info>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import StringIO
import unicodedata
import urllib
import zipfile

import nltk

SBLGNT_SOURCE = 'http://sblgnt.com/download/SBLGNTtxt.zip'

# Corpus book list
NT = ['Matt',
      'Mark',
      'Luke',
      'John',
      'Acts',
      'Rom',
      '1Cor',
      '2Cor',
      'Gal',
      'Eph',
      'Phil',
      'Col',
      '1Thess',
      '2Thess',
      '1Tim',
      '2Tim',
      'Titus',
      'Phlm',
      'Heb',
      'Jas',
      '1Pet',
      '2Pet',
      '1John',
      '2John',
      '3John',
      'Jude',
      'Rev']

# Filename lookup for books
FILENAMES = {'Matt': '61-Mt.txt',
             'Mark': '62-Mk.txt',
             'Luke': '63-Lk.txt',
             'John': '64-Jn.txt',
             'Acts': '65-Ac.txt',
             'Rom': '66-Ro.txt',
             '1Cor': '67-1Co.txt',
             '2Cor': '68-2Co.txt',
             'Gal': '69-Ga.txt',
             'Eph': '70-Eph.txt',
             'Phil': '71-Php.txt',
             'Col': '72-Col.txt',
             '1Thess': '73-1Th.txt',
             '2Thess': '74-2Th.txt',
             '1Tim': '75-1Ti.txt',
             '2Tim': '76-2Ti.txt',
             'Titus': '77-Tit.txt',
             'Phlm': '78-Phm.txt',
             'Heb': '79-Heb.txt',
             'Jas': '80-Jas.txt',
             '1Pet': '81-1Pe.txt',
             '2Pet': '82-2Pe.txt',
             '1John': '83-1Jn.txt',
             '2John': '84-2Jn.txt',
             '3John': '85-3Jn.txt',
             'Jude': '86-Jud.txt',
             'Rev': '87-Re.txt'}

def download(url):
    "Check the working directory for the source file and download if needed."
    
    if not os.path.exists(os.path.basename(url)):
        print "Downloading source file " + SBLGNT_SOURCE
        urllib.urlretrieve(url, os.path.basename(url))
    else:
        print "Source file " + os.path.basename(url) + " present."

def process_book(book,archive):
    "Return the normalized text of the given book."

    print "Processing " + book + "."
    filename = FILENAMES[book]
    pattern = re.compile('^.*\t')
    normalized = ""
    for line in StringIO.StringIO(archive.read(filename)):
        # Get rid of the leading verse number and \t character
        text = pattern.sub('',line)
        # Remove trailing whitespace (e.g. \r\n)
        text = text.strip()
        # Normalize unicode
        text = unicodedata.normalize("NFC", unicode(text, 'utf-8'))
        # Add back line break for proper tokenization later.
        normalized += text + "\n"
    f = open('out/' + book + '.txt','w')
    f.write(normalized.encode('utf8'))
    f.close()

def sblgnt_import():
    "Main process for importing SBLGNT text into NLTK."

    archive = zipfile.ZipFile(os.path.basename(SBLGNT_SOURCE))
    for book in NT:
        process_book(book,archive)
    
    print "Output files in 'out/'"
    
if __name__ == '__main__':
    # Create an output bin
    if not os.path.exists('out'):
        os.mkdir('out')
    download(SBLGNT_SOURCE)
    sblgnt_import()
