#!/usr/bin/env python3
#
# lxxm-layout.py
# Convert lxxmorph-unicode to have a layout similar to MorphGNT
# (c) 2014 Nathan D. Smith <nathan@smithfam.info>
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
import os


def convert_text(text):
    """Accepts an array of lxxmorph-unicode lines from a single book and
    returns an array of converted lines, or False on failure."""

    pass


def get_text(path):
    "Returns an array of UTF-8 encoded lines from the given file."

    try:
        f = codecs.open('out/' + path, encoding="utf-8")
        text = f.readlines()
        f.close()
        return text
    except:
        return False


def foo(bar):
    if not os.path.exists('plain'):
        os.mkdir('plain')
