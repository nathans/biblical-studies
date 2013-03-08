#! /usr/bin/env python
#
# lxxm-plain.py
# Outputs the Unicode LXXM text, one verse per-line.
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

import argparse
import codecs
import os
import unicodedata

def convert_file_to_plain(path):
    "Output the contents of the given LXXM file to plain text"

    print path
    if not os.path.exists('plain'):
        os.mkdir('plain')
    out_text = ""
    out_path = "plain/" + path
    f = codecs.open('out/' + path,encoding="utf-8")
    lines = f.readlines()
    f.close()
    verse = []
    for line in lines:
        
        # All word lines contain "-"
        if "-" in line:
            word = line.split()[0]
            verse.append(word)
    
        # Add blanklines
        elif line == "\n":
            line_text = " ".join(verse)
            line_text += "\n"
            out_text += line_text
            verse = []

    out_text = unicodedata.normalize("NFC", out_text)
    o = open(out_path,"w")
    o.write(out_text.encode("utf-8"))
    o.close()

if __name__ == '__main__':
    
    paths = os.listdir('out/')
    paths.sort()
    for path in paths:
        convert_file_to_plain(path)
