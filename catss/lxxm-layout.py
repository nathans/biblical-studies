#!/usr/bin/env python3
#
# lxxm-layout.py
# Convert lxxmorph-unicode to have a layout similar to MorphGNT
# (c) 2014, 2015 Nathan D. Smith <nathan@smithfam.info>
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

import codecs
import re
import os
import unicodedata

ref_pat_str = r'^(?P<book>[\w/]+) ?(?P<chapter>\d{1,3})?:?(?P<verse>\d{1,3})?'
ref_pat = re.compile(ref_pat_str)
verse_pat = re.compile(r'^(?P<verse>\d{1,3})?(?P<append>.*)')


def format_verse(text):
    "Accepts a raw verse string and return a properly-formatted verse string."

    verse_match = verse_pat.match(text)
    verse = int(verse_match.group("verse"))
    append = ""
    if verse_match.group("append"):
        append = verse_match.group("append")
    return "%03d%s" % (verse, append)


def convert_text(book_num, text):
    """Accepts a sequential book number and an array of lxxmorph-unicode
    lines from a single book and returns an array of converted lines,
    or False on failure.
    """

    out_lines = []
    verse = 0
    chapter = 0
    book = book_num
    verse_str = ""
    for line in text:
        verse_line = ref_pat.match(line)
        if verse_line:
            items = line.split()
            if len(items) > 1:
                if ":" not in items[1]:
                    chapter = 1
                    verse = format_verse(items[1])
                else:
                    ref = items[1].split(":")
                    # Handle Sirach
                    if ref[0] == "Prolog":
                        chapter = 0
                    else:
                        chapter = int(ref[0])
                    verse = format_verse(ref[1])
            else:
                chapter += 1
                verse = format_verse("0")
            verse_str = "%s%03d%s" % (book, int(chapter), verse)
        elif len(line.strip()) == 0:
            pass
        else:
            elements = line.strip().split()
            out_lines.append("%s %s %s %s" % (verse_str, elements[1],
                                              elements[0], elements[2]))
    return out_lines


def get_text(path):
    "Returns an array of UTF-8 encoded lines from the given file."

    try:
        f = codecs.open('out/' + path, encoding="utf-8")
        text = f.readlines()
        f.close()
        return text
    except:
        return False


if __name__ == "__main__":
    paths = os.listdir('out/')
    paths.sort()
    for path in paths:
        elems = path.split(".")
        lines = get_text(path)
        final = convert_text(elems[0], lines)
        out_path = "new/%s" % path
        out_text = ""
        for final_line in final:
            out_text += "%s\n" % final_line
        out_text = unicodedata.normalize("NFC", out_text)
        o = open(out_path, "w")
        o.write(out_text.encode("utf-8"))
        o.close()
