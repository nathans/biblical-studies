#! /usb/bin/env python
#
# sblgnt-corpus.py
# Create a tagged NLTK corpus from the SBLGNT
#
# (c) 2013 Nathan D. Smith <nathan@smithfam.info>
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

punctuation = [".",",",";",u"\u00b7"]

def convert(path):
    "Convert the given file to an NLTK tagged corpus file."

    if not os.path.exists('sblgnt-corpus'):
        os.mkdir('sblgnt-corpus')
    out_path = 'sblgnt-corpus/' + path.rsplit('-',1)[0]
    print "Converting " + out_path
    tokens = []
    f = codecs.open('source/' + path,encoding='utf-8')
    lines = f.readlines()
    f.close()
    for line in lines:
        fields = line.split()
        pos = fields[1].strip('-')
        parse = fields[2].replace('-','')
        tag = pos
        if len(parse) > 0:
            tag += '-' + parse
        token = fields[4] + '/' + tag
        tokens.append(token)
        # Deal with punctuation
        if fields[3][-1] in punctuation:
            punct = fields[3][-1]
            p_token = punct + '/' + punct
            tokens.append(p_token)
            if punct != ",":
                tokens.append("\n")

    text = ' '.join(tokens)
    g = open(out_path,'w')
    g.write(text.encode('utf-8'))
    g.close()
    
if __name__ == '__main__':
    paths = os.listdir('source/')
    paths.remove('README.md')
    paths.remove('.git')
    paths.sort()
    for path in paths:
        convert(path)
