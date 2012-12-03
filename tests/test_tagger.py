#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Tests for tagger.
"""

import unittest
from quepy import tagger


class TestTagger(unittest.TestCase):
    def test_tagset_unicode(self):
        for tag in tagger.PENN_TAGSET:
            self.assertIsInstance(tag, unicode)

    def test_word_encoding(self):
        word = tagger.Word(token=u"æßđħłłþłłł@æµß",
                           lemma=u"ŧłþłßæ#¶ŋħ~#~@",
                           pos=u"øĸŋøħþ€ĸłþ€øæ«»¢")

        self.assertIsInstance(word.token, unicode)
        self.assertEqual(word.token, u"æßđħłłþłłł@æµß")
        self.assertIsInstance(word.lemma, unicode)
        self.assertEqual(word.lemma, u"ŧłþłßæ#¶ŋħ~#~@")
        self.assertIsInstance(word.pos, unicode)
        self.assertEqual(word.pos, u"øĸŋøħþ€ĸłþ€øæ«»¢")

    def test_word_wrong_encoding(self):
        # Token not unicode
        self.assertRaises(ValueError, tagger.Word, "æßđħłłþłłł@æµß",
                          u"ŧłþłßæ#¶ŋħ~#~@", u"øĸŋøħþ€ĸłþ€øæ«»¢")
        # Lemma not unicode
        self.assertRaises(ValueError, tagger.Word, u"æßđħłłþłłł@æµß",
                          "ŧłþłßæ#¶ŋħ~#~@", u"øĸŋøħþ€ĸłþ€øæ«»¢")
        # Pos not unicode
        self.assertRaises(ValueError, tagger.Word, u"æßđħłłþłłł@æµß",
                          u"ŧłþłßæ#¶ŋħ~#~@", "øĸŋøħþ€ĸłþ€øæ«»¢")

    def test_word_attrib_set(self):
        word = tagger.Word(u"æßđħłłþłłł@æµß")
        word.lemma = u"ŧłþłßæ#¶ŋħ~#~@"
        word.pos = u"øĸŋøħþ€ĸłþ€øæ«»¢"

        self.assertIsInstance(word.token, unicode)
        self.assertEqual(word.token, u"æßđħłłþłłł@æµß")
        self.assertIsInstance(word.lemma, unicode)
        self.assertEqual(word.lemma, u"ŧłþłßæ#¶ŋħ~#~@")
        self.assertIsInstance(word.pos, unicode)
        self.assertEqual(word.pos, u"øĸŋøħþ€ĸłþ€øæ«»¢")

    def test_word_wrong_attrib_set(self):
        word = tagger.Word(u"æßđħłłþłłł@æµß")

        # Token not unicode
        self.assertRaises(ValueError, setattr, word, "token", "æßđħłłþłłł@æµß")
        # Lemma not unicode
        self.assertRaises(ValueError, setattr, word, "lemma", "ŧłþłßæ#¶ŋħ~#~@")
        # Pos not unicode
        self.assertRaises(ValueError, setattr, word, "pos", "øĸŋøħþ€ĸłþ€øæ«»¢")
