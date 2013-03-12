#! /usr/bin/env python
# coding=utf-8
#
# koine - a library for natural language processing for Koine Greek

import unicodedata

# List of stopwords obtained from Perseus Hopper source code and converted to
# UTF-8 with final sigmas.
# http://sourceforge.net/projects/perseus-hopper/
# Path: sgml/reading/properties/stoplists/greek.stop
stopwords = ["μή",
             "ἑαυτοῦ",
             "ἄν",
             "ἀλλ'",
             "ἀλλά",
             "ἄλλος",
             "ἀπό",
             "ἄρα",
             "αὐτός",
             "δ'",
             "δέ",
             "δή",
             "διά",
             "δαί",
             "δαίς",
             "ἔτι",
             "ἐγώ",
             "ἐκ",
             "ἐμός",
             "ἐν",
             "ἐπί",
             "εἰ",
             "εἰμί",
             "εἴμι",
             "εἰς",
             "γάρ",
             "γε",
             "ἡ",
             "ἤ",
             "καί",
             "κατά",
             "μέν",
             "μετά",
             "μή",
             "ὁ",
             "ὅδε",
             "ὅς",
             "ὅστις",
             "ὅτι",
             "οὕτως",
             "οὗτος",
             "οὔτε",
             "οὖν",
             "οὐδείς",
             "οἱ",
             "οὐ",
             "οὐδέ",
             "οὐκ",
             "περί",
             "πρός",
             "σύ",
             "σύν",
             "τά",
             "τε",
             "τήν",
             "τῆς",
             "τῇ",
             "τι",
             "τί",
             "τις",
             "τίς",
             "τό",
             "τοί",
             "τοιοῦτος",
             "τόν",
             "τούς",
             "τοῦ",
             "τῶν",
             "τῷ",
             "ὑμός",
             "ὑπέρ",
             "ὑπό",
             "ὡς",
             "ὦ",
             "ὥστε",
             "ἐάν",
             "παρά",
             "σός"]

def simplify_tag(tag):
    """Simplify the given tag, returning only the POS portion.

    This function may be given as the tag_mapping_function to the
    nltk.corpus.reader.TaggedCorpusReader (or similar) class. This allows the 
    argument simplify_tags=True to be passed to tagged_* methods on corpora."""

    # Derived from examples here:
    # http://nltk.googlecode.com/svn/trunk/doc/api/nltk.tag.simplify-pysrc.html

    try:
        if '-' in tag:
            tag = tag.split('-')[0]
        return tag
    except:
        return tag

def strip_diacritics(text):
    "Return the given text with diacritics removed."

    # http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    
    return ''.join([c for c in unicodedata.normalize('NFD',text) 
                    if unicodedata.category(c) != 'Mn'])
