#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Tests for Regex module.
"""

import unittest
from quepy.regex import RegexTemplate, Particle, Lemma
from quepy.tagger import Word


class Mockrule(object):
    rulename = "Mock"


class TestRegexTemplate(unittest.TestCase):
    def setUp(self):
        self.mockrule = Mockrule

        class SomeRegex(RegexTemplate):
            regex = Lemma(u"hello")

            def semantics(self, match):
                return Mockrule

        class SomeRegexWithData(RegexTemplate):
            regex = Lemma(u"hello")

            def semantics(self, match):
                return Mockrule, 42

        self.regexinstance = SomeRegex()
        self.regex_with_data = SomeRegexWithData()

    def test_match(self):
        words = [Word(u"hi", u"hello")]
        semantics, userdata = self.regexinstance.get_semantics(words)
        self.assertTrue(semantics is self.mockrule)
        self.assertEqual(userdata, None)

    def test_no_match(self):
        words = [Word(u"hi", u"hello"), Word(u"girl", u"girl")]
        semantics, userdata = self.regexinstance.get_semantics(words)
        self.assertEqual(semantics, None)
        self.assertEqual(userdata, None)

    def test_user_data(self):
        words = [Word(u"hi", u"hello")]
        _, userdata = self.regex_with_data.get_semantics(words)
        self.assertEqual(userdata, 42)

    def test_no_semantics(self):
        class SomeRegex(RegexTemplate):
            regex = Lemma(u"hello")

        regexinstance = SomeRegex()
        words = [Word(u"hi", u"hello")]
        self.assertRaises(NotImplementedError, regexinstance.get_semantics,
                          words)

    def test_regex_empty(self):
        class SomeRegex(RegexTemplate):
            def semantics(self, match):
                return Mockrule, "YES!"

        regexinstance = SomeRegex()
        words = [Word(u"hi", u"hello")]
        semantics, userdata = regexinstance.get_semantics(words)
        self.assertTrue(semantics is Mockrule)
        self.assertEqual(userdata, "YES!")

    def test_match_words(self):
        class SomeRegex(RegexTemplate):
            def semantics(self, match):
                return match

        words = [Word(u"|@€đ€łł@ð«|µnþ", u"hello"), Word(u"a", u"b", u"c")]
        match, _ = SomeRegex().get_semantics(words)
        self.assertEqual(words, match.words)


class TestParticle(unittest.TestCase):
    def setUp(self):
        class Person(Particle):
            regex = Lemma(u"Jim") | Lemma(u"Tonny")

            def semantics(self, match):
                return match

        class PersonRegex(RegexTemplate):
            regex = Person() + Lemma(u"be") + Person(u"another")

            def semantics(self, match):
                return match

        class PersonAsset(Person):
            regex = Person() + Lemma(u"'s") + Lemma(u"car")

        class NestedParticleRegex(PersonRegex):
            regex = PersonAsset() + Lemma(u"be") + Person(u"another")

        self.personregex = PersonRegex()
        self.nestedregex = NestedParticleRegex()

    def test_attrs(self):
        words = [Word(x, x) for x in u"Jim be Tonny".split()]
        match, _ = self.personregex.get_semantics(words)
        self.assertEqual(match.another.words[0], words[-1])
        self.assertEqual(match.person.words[0], words[0])
        self.assertRaises(AttributeError, lambda: match.pirulo)

    def test_nested_particle(self):
        words = [Word(x, x) for x in u"Jim 's car be Tonny".split()]
        match, _ = self.nestedregex.get_semantics(words)
        self.assertEqual(match.personasset.words[0], words[0])
        self.assertRaises(AttributeError, lambda: match.personasset.another)


if __name__ == "__main__":
    unittest.main()
