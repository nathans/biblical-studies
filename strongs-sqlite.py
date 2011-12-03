#! /usr/bin/env python
import xml.sax

hebrew_xml_file = ('../strongs/hebrew/StrongHebrewG.xml')

class StrongsParser(xml.sax.handler.ContentHandler):
    """Class to parse the Strongs xml files.

    https://github.com/openscriptures/strongs"""

    def __init__(self, db=None):
        self.in_foreign = False
        self.in_note = False
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
            self.in_note = True

        if name == "div" and attrs.getValue("type") == "entry":
            self.in_entry = True
        
        if name == "w" and self.in_foreign == False and self.in_note == False:
            #TODO need to find a way to screen for nested <note> tags
            self.number = attrs.getValue("ID")
            self.lemma = attrs.getValue("lemma")
            self.xlit = attrs.getValue("xlit")
            self.pronounce = attrs.getValue("POS")

    def characters(self, data):
        """Actions for characters within tags"""

        if self.in_note:
            self.description += data.replace("\n"," ")

    def endElement(self, name):
        """Actions for closing tags."""

        if name == "foreign":
            self.in_foreign = False

        if name == "note":
            self.in_note = False

        if name == "div" and self.in_entry == True:
            # Commit to db when each word's div tag is closed
            # Have to differentiate the type, since there is a div supertag.
            self.addRow()
            self.in_entry = False

if __name__ == "__main__":
    parser = xml.sax.make_parser()
    parser.setContentHandler(StrongsParser())
    f = open(hebrew_xml_file)
    parser.parse(f)


