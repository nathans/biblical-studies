#! /usr/bin/env python3
#
# lxxm-convert.py
# Download the CATSS LXXM files and convert them from betacode to unicode
# (c) 2013, 2014, 2016 Nathan D. Smith <nathan@smithfam.info>
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
from greekutils import beta2unicode
import codecs
import os
import re
import subprocess
import unicodedata
import urllib.request, urllib.parse, urllib.error

readme = """
The accompanying files are distributed by the Center for Computer
Analysis of Texts (CCAT) at the University of Pennsylvania for the use
of students, teachers and scholars in study and education contexts.
They are not to be used, either directly or indirectly, for commercial
purposes without prior written consent of the various legal authors
and developers identified below. If copies are made and given to other
persons for NON-COMMERCIAL use, those persons are also required to
register with CCAT by completing the standard "User Declaration" [1] and
returning it to CCAT at the address indicated on the form.

[1] http://ccat.sas.upenn.edu/gopher/text/religion/biblical/lxxmorph/0-user-declaration.txt
"""

base_url = "http://ccat.sas.upenn.edu/gopher/text/religion/biblical/lxxmorph/"
texts = ["01.Gen.1.mlxx",
         "02.Gen.2.mlxx",
         "03.Exod.mlxx",
         "04.Lev.mlxx",
         "05.Num.mlxx",
         "06.Deut.mlxx",
         "07.JoshB.mlxx",
         "08.JoshA.mlxx",
         "09.JudgesB.mlxx",
         "10.JudgesA.mlxx",
         "11.Ruth.mlxx",
         "12.1Sam.mlxx",
         "13.2Sam.mlxx",
         "14.1Kings.mlxx",
         "15.2Kings.mlxx",
         "16.1Chron.mlxx",
         "17.2Chron.mlxx",
         "18.1Esdras.mlxx",
         "19.2Esdras.mlxx",
         "20.Esther.mlxx",
         "21.Judith.mlxx",
         "22.TobitBA.mlxx",
         "23.TobitS.mlxx",
         "24.1Macc.mlxx",
         "25.2Macc.mlxx",
         "26.3Macc.mlxx",
         "27.4Macc.mlxx",
         "28.Psalms1.mlxx",
         "29.Psalms2.mlxx",
         "30.Odes.mlxx",
         "31.Proverbs.mlxx",
         "32.Qoheleth.mlxx",
         "33.Canticles.mlxx",
         "34.Job.mlxx",
         "35.Wisdom.mlxx",
         "36.Sirach.mlxx",
         "37.PsSol.mlxx",
         "38.Hosea.mlxx",
         "39.Micah.mlxx",
         "40.Amos.mlxx",
         "41.Joel.mlxx",
         "42.Jonah.mlxx",
         "43.Obadiah.mlxx",
         "44.Nahum.mlxx",
         "45.Habakkuk.mlxx",
         "46.Zeph.mlxx",
         "47.Haggai.mlxx",
         "48.Zech.mlxx",
         "49.Malachi.mlxx",
         "50.Isaiah1.mlxx",
         "51.Isaiah2.mlxx",
         "52.Jer1.mlxx",
         "53.Jer2.mlxx",
         "54.Baruch.mlxx",
         "55.EpJer.mlxx",
         "56.Lam.mlxx",
         "57.Ezek1.mlxx",
         "58.Ezek2.mlxx",
         "59.BelOG.mlxx",
         "60.BelTh.mlxx",
         "61.DanielOG.mlxx",
         "62.DanielTh.mlxx",
         "63.SusOG.mlxx",
         "64.SusTh.mlxx"]

beta_pat = r"[A-Z\\\(\)\*\|\+=/'#-]{,25}"
verse_pat = re.compile(r'^[\w/]+ ?(?P<chapter>\d{1,3})?:?(?P<verse>\d{1,3})?')
word_pat = re.compile(r"^(?P<word>" + beta_pat +
                      r")\s*(?P<morph>[\w \+/]{10})\s+(?P<root>("
                      + beta_pat + r"\s*)+)$")


def concatenate(text1, text2):
    "Concatenate text2 to text1, then delete text2"

    file2 = codecs.open('out/' + text2, encoding="utf-8")
    file2_txt = file2.read()
    file2.close()
    file1 = open('out/' + text1, "a")
    file1.write(file2_txt)
    file1.close()
    os.remove('out/' + text2)


def rename():
    "Combine and rename the books"

    # Genesis
    concatenate("01.Gen.1.txt", "02.Gen.2.txt")
    os.rename("out/01.Gen.1.txt", "out/01.Gen.txt")
    # Psalms
    concatenate("28.Psalms1.txt", "29.Psalms2.txt",)
    os.rename("out/28.Psalms1.txt", "out/28.Psalms.txt")
    # Isaiah
    concatenate("50.Isaiah1.txt", "51.Isaiah2.txt")
    os.rename("out/50.Isaiah1.txt", "out/50.Isaiah.txt")
    # Jeremiah
    concatenate("52.Jer1.txt", "53.Jer2.txt")
    os.rename("out/52.Jer1.txt", "out/52.Jer.txt")
    # Ezekiel
    concatenate("57.Ezek1.txt", "58.Ezek2.txt")
    os.rename("out/57.Ezek1.txt", "out/57.Ezek.txt")

    # Renumber
    i = 0
    books = os.listdir('out/')
    books.sort()
    for path in books:
        i += 1
        book = path.split(".", 1)[1]
        os.rename('out/' + path, 'out/{:0>2}.{}'.format(i, book))


def download_lxxm():
    "Download the collection of lxxmorph files"

    print("Retrieving texts")
    print(readme)
    if not os.path.exists('source/'):
        os.mkdir('source')
    for text in texts:
        url = base_url + text
        if not os.path.exists('source/' + os.path.basename(url)):
            print(text)
            urllib.request.urlretrieve(url, 'source/' + os.path.basename(url))


def to_unicode(betacode):
    "Convert the given betacode and returns equivalent unicode"

    # Correct for final sigma
    if "S-" in betacode or "S " in betacode:
        betacode = betacode.replace("S-", "S\n-")
        betacode = betacode.replace("S ", "S\n ")
    if betacode.endswith('S'):
        betacode += "\n"
    unicode_txt = beta2unicode.convert(betacode)
    return unicodedata.normalize("NFC", unicode_txt)


def convert_file(path):
    "Convert the contents of the file from betacode to unicode"

    if not os.path.exists('out'):
        os.mkdir('out')
    out_path = "out/" + path.rsplit(".", 1)[0] + ".txt"
    print(out_path)
    out_text = ""
    # Book, chapter, verse, and (all together) refrent not implemented yet
    # book = path[0:2]
    # chapter = ""
    # verse = ""
    # ref = ""
    f = open('source/' + path)
    lines = f.readlines()
    f.close()
    for line in lines:
        verse_line = None
        # All word lines are longer than 25 characters, the width of 1st column
        if len(line) < 25:
            verse_line = verse_pat.match(line)
        word_line = word_pat.search(line)

        if verse_line:
            out_text += line

        elif word_line:
            beta_word = word_line.group('word')
            morph = word_line.group('morph')
            # Ensure that morph tags are not missed by the parser
            if (not morph) or (morph == "          "):
                print("Missed morph")
                raise Exception
            beta_root = word_line.group('root').split()

            # Replace whitespace in morph with -
            morph = morph.replace(" ", "-")

            word = to_unicode(beta_word)
            output = "{} {}".format(word, morph)
            # Add each part of the root
            for part in beta_root:
                # Correct for '+' in root in some instances
                crasis = False
                if (("+" in part) and (("+" in morph) or
                                       (morph.startswith("M")) or
                                       (morph.startswith("X")) or
                                       ("-" in beta_word))
                    and ("+" not in beta_word)):
                    crasis = True
                    part = part.replace("+", " ")
                rt = to_unicode(part)
                if crasis:
                    rt = rt.replace(" ", "+")
                output += " " + rt
            out_text += output + "\n"

        elif line == "\n":
            out_text += line

        elif line != "\n":
            print("Missed line: " + line)
            raise Exception

    o = open(out_path, "w")
    o.write(out_text)
    o.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Convert the CATSS LXXM text to unicode")
    subs = parser.add_subparsers(dest='command')
    # Download
    parser_dl = subs.add_parser("download", help="Download the files")
    # Patch
    parser_diff = subs.add_parser("patch", help="Apply corrections")
    # Convert
    parser_conv = subs.add_parser("convert",
                                  help="Convert from betacode to unicode")
    # Rename
    parser_ren = subs.add_parser("rename", help="Rename files")
    # All
    parser_all = subs.add_parser("all", help="Complete all actions")
    args = parser.parse_args()

    if args.command == "download" or args.command == "all":
        download_lxxm()
    # Apply corrections so unicode conversion will work
    if args.command == "patch" or args.command == "all":
        subprocess.call("patch -p1 < lxxm-corrections.patch", shell=True)
    if args.command == "convert" or args.command == "all":
        for text in texts:
            convert_file(text)
    if args.command == "rename" or args.command == "all":
        rename()
