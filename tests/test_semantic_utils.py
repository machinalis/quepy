#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Tests for semantic utils.
"""

import unittest

from quepy.tagger import Word
from quepy import semantic_utils
from quepy.semantics import HasKeyword, FixedType


class TestSemanticUtils(unittest.TestCase):

    def test_handle_keywords_invalid_input(self):
        self.assertRaises(ValueError, semantic_utils.handle_keywords,
                          "not unicode text")

    def test_handle_keywords(self):
        output = semantic_utils.handle_keywords(u"uranium blowtorch")
        self.assertIsInstance(output, HasKeyword)

        keywords = [x[1] for x in output.nodes[0]]
        self.assertIn(u"uranium", keywords)
        self.assertIn(u"blowtorch", keywords)

    def test_nounlike_noun(self):
        noun_word = Word(u"dog", u"dog", u"NN")
        output = semantic_utils.handle_nounlike(noun_word)
        self.assertIsInstance(output, HasKeyword)
        noun_word = Word(u"dog", u"dog", u"NNP")
        output = semantic_utils.handle_nounlike(noun_word)
        self.assertIsInstance(output, HasKeyword)

    def test_nounlike_handler(self):
        from quepy import handlers

        class DogType(FixedType):
            fixedtype = "dog"

        class MyHandler(handlers.Handler):
            def check(self, word):
                return word.lemma == "special_dog"

            def handler(self, word):
                return DogType()

        handlers.register(MyHandler)
        noun_word = Word(u"lazzy", u"special_dog", u"NN")
        output = semantic_utils.handle_nounlike(noun_word)
        self.assertIsInstance(output, DogType)

    def test_nounlike_unhandled(self):
        non_noun_word = Word(u"ran", u"run", u"VB")
        self.assertRaises(semantic_utils.UnhandledWord,
                          semantic_utils.handle_nounlike,
                          non_noun_word)

    def test_handle_noun_phrase(self):
        noun_phrase = [Word(u"cool", u"cool", u"JJ"),
                       Word(u"dogs", u"dog", u"NNS")]
        output = semantic_utils.handle_noun_phrase(noun_phrase)
        self.assertIsInstance(output, HasKeyword)


if __name__ == "__main__":
    unittest.main()
