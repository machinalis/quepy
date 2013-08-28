# -*- coding: utf-8 -*-

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

import unittest
from quepy.generation import get_code
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


class TestCodeGeneration(unittest.TestCase):

    def _standard_check(self, s, e):
        self.assertIsInstance(s, unicode)
        vs = [u"x{}".format(i) for i in xrange(len(e))]
        for var in vs:
            self.assertIn(var, s)

    def test_dot_takes_unicode(self):
        e = gen_fixedtype(u"·̣─@łæßð~¶½")
        e += gen_datarel(u"tµŧurułej€", u"←ðßðæßđæßæđßŋŋæ @~~·ŋŋ·¶·ŋ“¶¬@@")
        _, s = get_code(e, "dot")
        self._standard_check(s, e)

    def test_dot_takes_fails_ascii1(self):
        e = gen_fixedtype("a")
        e += gen_datarel("b", "c")
        e = gen_fixedrelation("d", e)
        self.assertRaises(ValueError, get_code, e, "dot")

    def test_dot_takes_fails_ascii2(self):
        e = gen_fixedtype("·̣─@łæßð~¶½")
        e += gen_datarel("tµŧurułej€", "←ðßðæßđæßæđßŋŋæ @~~·ŋŋ·¶·ŋ“¶¬@@")
        self.assertRaises(ValueError, get_code, e, "dot")

    def test_sparql_takes_unicode(self):
        e = gen_fixedtype(u"·̣─@łæßð~¶½")
        e += gen_datarel(u"tµŧurułej€", u"←ðßðæßđæßæđßŋŋæ @~~·ŋŋ·¶·ŋ“¶¬@@")
        _, s = get_code(e, "sparql")
        self._standard_check(s, e)

    def test_sparql_takes_fails_ascii1(self):
        e = gen_fixedtype("a")
        e += gen_datarel("b", "c")
        e = gen_fixedrelation("d", e)
        self.assertRaises(ValueError, get_code, e, "sparql")

    def test_sparql_takes_fails_ascii2(self):
        e = gen_fixedtype("·̣─@łæßð~¶½")
        e += gen_datarel("tµŧurułej€", "←ðßðæßđæßæđßŋŋæ @~~·ŋŋ·¶·ŋ“¶¬@@")
        self.assertRaises(ValueError, get_code, e, "sparql")


if __name__ == "__main__":
    unittest.main()
