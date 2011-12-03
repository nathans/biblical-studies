#! /usr/bin/env python
#
# Strongs XML to sqlite3 converter
# Copyright (c) 2011 Nathan Smith <nathan@smithfam.info>
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

import xml.sax

hebrew_xml_file = '../strongs/hebrew/StrongHebrewG.xml'
greek_xml_file = '../strongs/greek/StrongsGreekDictionaryXML_1.4/strongsgreek.xml'

class StrongsHebrewParser(xml.sax.handler.ContentHandler):
    """Class to parse the Strongs Hebrew xml files.

    https://github.com/openscriptures/strongs"""

    def __init__(self, db=None):
        self.in_foreign = False
        self.note_depth = 0
        self.in_entry = False
        self.db = db
        self.reset_vars()

    def reset_vars(self):
        self.number = ""
        self.lemma = ""
        self.xlit = ""
        self.pronounce = ""
        self.description = ""

    def addRow(self):
       print "%s|%s|%s|%s|%s" % (self.number, self.lemma, self.xlit,
                              self.pronounce, self.description)
       self.reset_vars()

    def startElement(self, name, attrs):
        """Actions for opening tags."""

        if name == "foreign":
            self.in_foreign = True

        if name == "note":
            self.note_depth +=1

        if name == "div" and attrs.getValue("type") == "entry":
            self.in_entry = True
        
        if name == "w" and self.in_foreign == False and self.note_depth == 0:
            self.number = attrs.getValue("ID")
            self.lemma = attrs.getValue("lemma")
            self.xlit = attrs.getValue("xlit")
            self.pronounce = attrs.getValue("POS")

    def characters(self, data):
        """Actions for characters within tags"""

        if self.note_depth > 0:
            self.description += data.replace("\n"," ")

    def endElement(self, name):
        """Actions for closing tags."""

        if name == "foreign":
            self.in_foreign = False

        if name == "note":
            self.note_depth -=1

        if name == "div" and self.in_entry == True:
            # Commit to db when each word's div tag is closed
            # Have to differentiate the type, since there is a div supertag.
            self.addRow()
            self.in_entry = False

if __name__ == "__main__":
    hebrew_parser = xml.sax.make_parser()
    hebrew_parser.setContentHandler(StrongsHebrewParser())
    h = open(hebrew_xml_file)
    hebrew_parser.parse(h)

# TODO
# - Add sqlite3 integration
