#! /usb/bin/env python
#
# sblgnt-corpus.py
# Create a tagged NLTK corpus from the SBLGNT
#
# (c) 2013, 2015 Nathan D. Smith <nathan@smithfam.info>
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
import os

import pysblgnt

punctuation = [".", ",", ";", "\u00b7"]


def convert(book_num):
    "Convert the given file to an NLTK tagged corpus file."

    if not os.path.exists('sblgnt-corpus'):
        os.mkdir('sblgnt-corpus')

    # Use the built-in filename function, but omit the leading path
    book_path = pysblgnt.morphgnt_filename(book_num).split("/")[1]
    out_path = 'sblgnt-corpus/' + book_path.rsplit('-', 1)[0]
    print("Converting " + out_path)
    tokens = []
        
    for line in pysblgnt.morphgnt_rows(book_num):
        pos = line["ccat-pos"].strip('-')
        parse = line["ccat-parse"].replace('-', '')
        tag = pos
        if len(parse) > 0:
            tag += '-' + parse
        token = line["word"] + '/' + tag
        tokens.append(token)
        # Deal with punctuation
        if line["text"][-1] in punctuation:
            punct = line["text"][-1]
            p_token = punct + '/' + punct
            tokens.append(p_token)
            if punct != ",":
                tokens.append("\n")

    text = ' '.join(tokens)
    g = open(out_path, 'w')
    g.write(text)
    g.close()

if __name__ == '__main__':
    for book_num in range(27):
        convert(book_num+1)
