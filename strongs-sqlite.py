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
import sqlite3
import xml.sax

hebrew_xml = '../strongs/hebrew/StrongHebrewG.xml'
greek_xml = '../strongs/greek/StrongsGreekDictionaryXML_1.4/strongsgreek.xml'
db_file = 'strongs.sqlite'
log_file = 'strongs.log'


class StrongsDB():
    """Class to handle database access for Strongs import"""

    def __init__(self, db_file):
        """Initialize the database and instance vars."""
        self.reset_vars()
        self._conn = sqlite3.connect(db_file)
        self._cursor = self._conn.cursor()
        init_db_sql = "create table strongs (number text, lemma text, \
            xlit text, pronounce text, deriv text, defin text, trans text)"
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
        self.deriv = ""
        self.defin = ""
        self.trans = ""
    
    def add_row(self):
        """Add a full row into the database, used for Hebrew."""
        add_row_sql = 'insert into strongs values (?, ?, ?, ?, ?, ?, ?)' 
        logging.debug("add_row_sql: %s|%s|%s|%s|%s|%s|%s" % (self.number, 
            self.lemma, self.xlit, self.pronounce, self.deriv, 
            self.defin, self.trans))
        self._cursor.execute(add_row_sql, (self.number, self.lemma, self.xlit, 
            self.pronounce, self.deriv, self.defin, self.trans,))
        self.reset_vars()

    def add_row_greek(self):
        """Add a partial line, lacking derivation, for Greek."""
        arg_sql = "insert into strongs (number, lemma, xlit, pronounce, defin,\
            trans) values (?, ?, ?, ?, ?, ?)"
        logging.debug("add_row_sql: %s|%s|%s|%s|%s|%s" % (self.number, 
            self.lemma, self.xlit, self.pronounce, self.defin, self.trans))
        self._cursor.execute(arg_sql, (self.number, self.lemma, self.xlit, 
            self.pronounce, self.defin, self.trans,))
        self.reset_vars()

    def add_deriv(self):
        """Fill in the missing deriv field for Greek."""
        ad_sql = "update strongs set deriv = ? where number = ?"
        logging.debug("updating %s with deviv: %s" % (self.number, self.deriv))
        self._cursor.execute(ad_sql, (self.deriv, self.number,))
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
        self.in_deriv = False
        self.in_defin = False
        self.in_trans = False
        self.buffer = ""
        self.db = db

    def startElement(self, name, attrs):
        """Actions for opening tags."""
        if name == "foreign":
            self.in_foreign = True
        if name == "note":
            self.note_depth +=1
            if attrs.getValue("type") == "exegesis":
                self.in_deriv = True
            elif attrs.getValue("type") == "explanation":
                self.in_defin = True
            elif attrs.getValue("type") == "translation":
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
                self.buffer += attrs.getValue("lemma")
            else:
                self.buffer += attrs.getValue("POS")

    def characters(self, data):
        """Actions for characters within tags"""
        if self.note_depth > 0:
            self.buffer += data

    def endElement(self, name):
        """Actions for closing tags."""
        if name == "foreign":
            self.in_foreign = False
        if name == "note":
            self.note_depth -=1
            # If we exit a note completely, close the note types
            if self.note_depth == 0:
                if self.in_deriv:
                    self.db.deriv = self.buffer
                elif self.in_defin:
                    self.db.defin = self.buffer
                elif self.in_trans:
                    self.db.trans = self.buffer
                # All note types can be closed, and buffer reset
                self.buffer = ""
                self.in_deriv = False
                self.in_defin = False
                self.in_trans = False
        if name == "div" and self.in_entry == True:
            # Commit to db when each word's div tag is closed
            # Have to differentiate the type, since there is a div supertag.
            self.db.add_row()
            self.in_entry = False


class StrongsGreekParser(xml.sax.handler.ContentHandler):
    """Class to parse the Strongs Greek xml file."""

    def __init__(self, db):
        self.in_entry = False
        self.in_strongs = False
        self.in_defin = False
        self.in_trans = False
        self.db = db
    def startElement(self, name, attrs):
        """Actions for opening tags."""
        if name == "entry":
            self.in_entry = True
        if name == "strongs":
            self.in_strongs = True
        if name == "greek":
            self.db.lemma = attrs.getValue("unicode")
            self.db.xlit = attrs.getValue("translit")
        if name == "pronunciation":
            self.db.pronounce = attrs.getValue("strongs")
        if name == "strongs_def":
            self.in_defin = True
        if name == "kjv_def":
            self.in_trans = True

    def characters(self, data):
        """Actions for characters within tags"""
        if self.in_strongs:
            self.db.number = "G%s" % data
        if self.in_defin:
            self.db.defin += data
        if self.in_trans:
            self.db.trans += data

    def endElement(self, name):
        """Actions for closing tags."""
        if name == "entry":
            self.in_entry = False
            self.db.add_row_greek()
        if name == "strongs":
            self.in_strongs = False
        if name == "strongs_def":
            self.in_defin = False
        if name == "kjv_def":
            self.in_trans = False


class StrongsG2Parser(xml.sax.handler.ContentHandler):
    """Class to fill in strongs_derivation in Greek from db."""

    def __init__(self, db):
        self.in_deriv = False
        self.in_strongs = False
        self.db = db

    def startElement(self, name, attrs):
        """Actions for opening tags."""
        if name == "strongs_derivation":
            self.in_deriv = True
        if name == "strongs":
            self.in_strongs = True
        if name == "strongsref":
            lang = attrs.getValue("language")
            num = attrs.getValue("strongs").lstrip("0")
            number = "%s%s" % (lang[0], num)
            logging.debug("Querying strongsref %s for entry %s" % (number, 
                self.db.number))
            lemma = self.db.get_lemma(number)
            self.db.deriv += lemma

    def characters(self, data):
        """Actions for characters within tags"""
        if self.in_deriv:
            self.db.deriv += data
        if self.in_strongs:
            self.db.number = "G%s" % data

    def endElement(self, name):
        """Actions for closing tags."""
        if name == "entry":
            self.db.add_deriv()
        if name == "strongs_derivation":
            self.in_deriv = False
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
