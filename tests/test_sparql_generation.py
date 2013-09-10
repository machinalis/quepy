# -*- coding: utf-8 -*-

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

import re
import unittest
from random_expression import random_expression
from random import seed
from quepy.sparql_generation import expression_to_sparql
from quepy.dsl import FixedRelation, FixedType, \
    FixedDataRelation


def gen_datarel(rel, data):
    class X(FixedDataRelation):
        relation = rel
    return X(data)


def gen_fixedtype(type_):
    class X(FixedType):
        fixedtype = type_
    return X()


def gen_fixedrelation(rel, e):
    class X(FixedRelation):
        relation = rel
    return X(e)


class TestSparqlGeneration(unittest.TestCase):

    _sparql_line = re.compile("\?x\d+ \S+ (?:\?x\d+|\".*\"|\S+?:\S+?)"
                              "(?:@\w+)?.", re.DOTALL)
    _sparql_query_start = re.compile("SELECT DISTINCT .+ WHERE {(.+)}",
                                     re.DOTALL)

    def _standard_check(self, s, e):
        self.assertIsInstance(s, unicode)
        vs = [u"x{}".format(i) for i in xrange(len(e))]
        for var in vs:
            self.assertIn(var, s)

    def _sparql_check(self, s):
        m = self._sparql_query_start.search(s)
        self.assertNotEqual(m, None, "Could not find query start ")
        lines = m.group(1).split("\n")
        for line in lines:
            line = line.strip()
            if line:
                s = "Line out of format: {!r}\n".format(line)
                self.assertNotEqual(self._sparql_line.match(line), None, s)

    def test_sparql_takes_unicode(self):
        e = gen_fixedtype(u"·̣─@łæßð~¶½")
        e += gen_datarel(u"tµŧurułej€", u"←ðßðæßđæßæđßŋŋæ @~~·ŋŋ·¶·ŋ“¶¬@@")
        _, s = expression_to_sparql(e)
        self._standard_check(s, e)
        self._sparql_check(s)

    @unittest.skip("should be fixed")
    def test_sparql_ascii_stress(self):
        seed("sacala dunga dunga dunga")
        for _ in xrange(100):
            expression = random_expression(only_ascii=True)
            _, s = expression_to_sparql(expression)
            self._standard_check(s, expression)
            self._sparql_check(s)

    def test_sparql_stress(self):
        seed("sacala dunga dunga dunga")
        for _ in xrange(100):
            expression = random_expression()
            try:
                _, s = expression_to_sparql(expression)
            except ValueError as error:
                if "Unable to generate sparql" in str(error):
                    continue

            self._standard_check(s, expression)
            self._sparql_check(s)

    def test_sparql_takes_fails_ascii1(self):
        e = gen_fixedtype("a")
        e += gen_datarel("b", "c")
        e = gen_fixedrelation("d", e)
        self.assertRaises(ValueError, expression_to_sparql, e)

    def test_sparql_takes_fails_ascii2(self):
        e = gen_fixedtype("·̣─@łæßð~¶½")
        e += gen_datarel("tµŧurułej€", "←ðßðæßđæßæđßŋŋæ @~~·ŋŋ·¶·ŋ“¶¬@@")
        self.assertRaises(ValueError, expression_to_sparql, e)


if __name__ == "__main__":
    unittest.main()
