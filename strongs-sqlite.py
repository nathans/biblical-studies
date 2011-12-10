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

import logging
import os
import sqlite3
import StringIO
import xml.sax
import zipfile
import urllib


hebrew_xml = 'https://github.com/openscriptures/strongs/raw/master/hebrew/StrongHebrewG.xml'
greek_zip = 'http://files.morphgnt.org/strongs-dictionary/StrongsGreekDictionaryXML_1.5.zip'
dbb_file = 'strongs.sqlite'
log_file = 'strongs.log'


class StrongsDB():
    """Class to handle database access for Strongs import"""

    def __init__(self, db_file):
        """Initialize the database and instance vars."""
        self.reset_vars()
        self._conn = sqlite3.connect(db_file)
        self._cursor = self._conn.cursor()
        init_db_sql = "create table strongs (number text, lemma text, \
            xlit text, pronounce text, description text)"
        self._cursor.execute(init_db_sql)
        self._conn.commit()

    def reset_vars(self):
        """Reset instance variables between db operations.

        Should be called after batches of add_row, add_row_greek, and
        add_deriv.
        """
        self.number = ""
        self.lemma = ""
        self.xlit = ""
        self.pronounce = ""
        self.description = ""
    
    def add_row(self):
        """Add a full row into the database, used for Hebrew."""
        add_row_sql = 'insert into strongs values (?, ?, ?, ?, ?)' 
        logging.debug("add_row_sql: %s|%s|%s|%s|%s" % (self.number, 
            self.lemma, self.xlit, self.pronounce, self.description))
        self._cursor.execute(add_row_sql, (self.number, self.lemma, self.xlit, 
            self.pronounce, self.description,))
        self.reset_vars()

    def add_row_greek(self):
        """Add a partial line, lacking derivation, for Greek."""
        arg_sql = "insert into strongs (number, lemma, xlit, pronounce) values\
            (?, ?, ?, ?)"
        logging.debug("add_row_sql: %s|%s|%s|%s" % (self.number, 
            self.lemma, self.xlit, self.pronounce))
        self._cursor.execute(arg_sql, (self.number, self.lemma, self.xlit, 
            self.pronounce,))
        self.reset_vars()

    def add_deriv(self):
        """Fill in the missing deriv field for Greek."""
        self.prepare_row()
        ad_sql = "update strongs set description = ? where number = ?"
        logging.debug("updating %s with description: %s" % (self.number,
                                                      self.description))
        self._cursor.execute(ad_sql, (self.description, self.number,))
        self.reset_vars()

    def get_lemma(self, number):
        """Query the database for the given number and return the lemma.

        If the database does not have the lemma for that number, return the
        number back instead.
        """
        gl_sql = "select lemma from strongs where number=?"
        self._cursor.execute(gl_sql, (number,))
        res = self._cursor.fetchone()
        if not res:
            lemma = number
        else:
            lemma = res[0]
        return lemma

    def prepare_row(self):
        self.description = self.description.replace("\n","")

    def db_commit(self):
        """Commit changes to the database."""
        self._conn.commit()

    def finish(self):
        """Close the database connection."""
        self._cursor.close()


class StrongsHebrewParser(xml.sax.handler.ContentHandler):
    """Class to parse the Strongs Hebrew xml file."""

    def __init__(self, db):
        self.in_foreign = False
        self.note_depth = 0
        self.in_entry = False
        self.in_trans = False
        self.db = db

    def startElement(self, name, attrs):
        """Actions for opening tags."""
        if name == "foreign":
            self.in_foreign = True
        if name == "note":
            self.note_depth +=1
            if attrs.getValue("type") == "translation":
                self.in_trans = True
        if name == "div" and attrs.getValue("type") == "entry":
            self.in_entry = True
        if name == "w" and self.in_foreign == False and self.note_depth == 0:
            self.db.number = attrs.getValue("ID")
            self.db.lemma = attrs.getValue("lemma")
            self.db.xlit = attrs.getValue("xlit")
            self.db.pronounce = attrs.getValue("POS")
        if name == "w" and self.note_depth > 0:
            if "lemma" in attrs.getNames():
                self.db.description += attrs.getValue("lemma")
            else:
                self.db.description += attrs.getValue("POS")

    def characters(self, data):
        """Actions for characters within tags"""
        if self.note_depth > 0:
            self.db.description += data

    def endElement(self, name):
        """Actions for closing tags."""
        if name == "foreign":
            self.in_foreign = False
        if name == "note":
            self.note_depth -=1
            # If we exit a note completely, close the note types
            if self.note_depth == 0 and not self.in_trans:
                # Add a space between entries when moving between notes
                if self.db.description and self.db.description[-1] == ";":
                    self.db.description += " "
                else:
                    self.db.description += "; "
        if name == "div" and self.in_entry == True:
            # Commit to db when each word's div tag is closed
            # Have to differentiate the type, since there is a div supertag.
            self.db.add_row()
            self.in_entry = False
            self.in_trans = False


class StrongsGreekParser(xml.sax.handler.ContentHandler):
    """Class to parse the Strongs Greek xml file."""

    def __init__(self, db):
        self.in_entry = False
        self.in_strongs = False
        self.greek_tag = 0
        self.db = db

    def startElement(self, name, attrs):
        """Actions for opening tags."""
        if name == "entry":
            self.in_entry = True
        if name == "strongs":
            self.in_strongs = True
        if name == "greek":
            # Ignore <greek> tags after the first one.
            # Corrects a bug in G1
            self.greek_tag += 1
            if self.greek_tag == 1:
                self.db.lemma = attrs.getValue("unicode")
                self.db.xlit = attrs.getValue("translit")
        if name == "pronunciation":
            self.db.pronounce = attrs.getValue("strongs")

    def characters(self, data):
        """Actions for characters within tags"""
        if self.in_strongs:
            self.db.number = "G%s" % data
        
    def endElement(self, name):
        """Actions for closing tags."""
        if name == "entry":
            self.in_entry = False
            self.greek_tag = 0
            self.db.add_row_greek()
        if name == "strongs":
            self.in_strongs = False


class StrongsG2Parser(xml.sax.handler.ContentHandler):
    """Class to fill in strongs_derivation in Greek from db."""

    def __init__(self, db):
        self.in_desc = False
        self.in_strongs = False
        self.db = db

    def startElement(self, name, attrs):
        """Actions for opening tags."""
        if name == "strongs_derivation":
            self.in_desc = True
        if name == "strongs":
            self.in_strongs = True
        if name == "strongsref":
            lang = attrs.getValue("language")
            num = attrs.getValue("strongs").lstrip("0")
            number = "%s%s" % (lang[0], num)
            logging.debug("Querying strongsref %s for entry %s" % (number, 
                self.db.number))
            lemma = self.db.get_lemma(number)
            self.db.description += lemma

    def characters(self, data):
        """Actions for characters within tags"""
        if self.in_desc:
            self.db.description += data
        if self.in_strongs:
            self.db.number = "G%s" % data

    def endElement(self, name):
        """Actions for closing tags."""
        if name == "entry":
            self.db.add_deriv()
        if name == "entry":
            self.in_desc = False
        if name == "strongs":
            self.in_strongs = False


if __name__ == "__main__":
    # Configure log level here
    logging.basicConfig(level=logging.DEBUG, filename=log_file)
    # Initialize the db here
    db = StrongsDB(db_file)
    # Parse the Hebrew here
    logging.info("Parsing Hebrew XML")
    hebrew_parser = xml.sax.make_parser()
    hebrew_parser.setContentHandler(StrongsHebrewParser(db))
    h = open(hebrew_xml)
    hebrew_parser.parse(h)
    h.close()
    db.db_commit()
    # Parse the Greek here
    logging.info("Parsing Greek XML")
    greek_parser = xml.sax.make_parser()
    greek_parser.setContentHandler(StrongsGreekParser(db))
    g = open(greek_xml)
    greek_parser.parse(g)
    g.close()
    db.db_commit()
    # Second pass on the Greek to retrieve missing lemmas in strongs_derivation
    logging.info("Finish Greek Strongs derivations")
    g2_parser = xml.sax.make_parser()
    g2_parser.setContentHandler(StrongsG2Parser(db))
    g2 = open(greek_xml)
    g2_parser.parse(g2)
    g2.close()
    db.db_commit()
    # All Done
    logging.info("Finished. sqlite database at %s is ready." % db_file)
