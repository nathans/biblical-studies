#! /usb/bin/env python3
#
# lxxm-corpus.py
# Create a tagged NLTK corpus from the LXXM
# Derived from sblgnt-corpus.py
#
# (c) 2013, 2014, 2016 Nathan D. Smith <nathan@smithfam.info>
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
import re


def convert(path):
    "Convert the given file to an NLTK tagged corpus file."

    if not os.path.exists('lxxm-corpus'):
        os.mkdir('lxxm-corpus')
    out_path = 'lxxm-corpus/' + path.rsplit('-', 1)[0]
    print("Converting " + out_path)
    tokens = []
    f = codecs.open('source/' + path, encoding='utf-8')
    lines = f.readlines()
    f.close()
    for line in lines:
        # Handle verse lables
        if re.match(r"^[A-Z]", line):
            pass
        # Empty lines signify verse breaks, treat as sentence breaks
        elif re.match(r"\n", line):
            tokens.append("\n")
        else:
            fields = line.split()
            pos = fields[1][:3].replace('-', '')
            parse = fields[1][3:].replace('-', '')
            tag = pos
            if len(parse) > 0:
                tag += '-' + parse
            token = fields[0] + '/' + tag
            tokens.append(token)

    text = ' '.join(tokens)
    g = open(out_path, 'w')
    g.write(text)
    g.close()

if __name__ == '__main__':
    # Obtain list of files
    paths = os.listdir('source/')
    # Remove meta files
    paths.remove('README-Unicode')
    paths.remove('.git')
    paths.remove('*Morph-Coding')
    paths.remove('*ReadMe.Analysis')
    paths.remove('0-readme.txt')
    paths.remove('0-user-declaration.txt')

    paths.sort()
    for path in paths:
        convert(path)
