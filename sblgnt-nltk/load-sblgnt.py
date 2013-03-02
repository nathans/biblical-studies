# load-sblgnt.py
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

import codecs
import nltk
import os

nt = ""
texts = os.listdir('out/')

for text in texts:
    f = codecs.open('out/' + text,encoding='utf-8')
    nt += f.read()
    f.close()

# Need to avoid using default wordpunct tokenizer here, since it erroneously
# splits elisions from tokens.
# \u2019 is the character used by SBLGNT for elisions, so it is added
nt_tokens = nltk.tokenize.regexp.regexp_tokenize(nt, 
                                                 u'\w+\u2019?|[^\w\s\u2019]+')
sblgnt_text = nltk.text.Text([w.encode('utf-8') for w in nt_tokens])
sblgnt_text.collocations()
sblgnt_text.generate()
