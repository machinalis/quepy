# -*- coding: utf-8 -*-

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

import unittest
import tempfile
import subprocess
from random_expression import random_expression
from random import seed
from quepy.dot_generation import expression_to_dot
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


class TestDotGeneration(unittest.TestCase):

    def _standard_check(self, s, e):
        self.assertIsInstance(s, unicode)
        vs = [u"x{}".format(i) for i in xrange(len(e))]
        for var in vs:
            self.assertIn(var, s)

    def test_dot_takes_unicode(self):
        e = gen_fixedtype(u"·̣─@łæßð~¶½")
        e += gen_datarel(u"tµŧurułej€", u"←ðßðæßđæßæđßŋŋæ @~~·ŋŋ·¶·ŋ“¶¬@@")
        _, s = expression_to_dot(e)
        self._standard_check(s, e)

    def test_dot_takes_fails_ascii1(self):
        e = gen_fixedtype("a")
        e += gen_datarel("b", "c")
        e = gen_fixedrelation("d", e)
        self.assertRaises(ValueError, expression_to_dot, e)

    def test_dot_takes_fails_ascii2(self):
        e = gen_fixedtype("·̣─@łæßð~¶½")
        e += gen_datarel("tµŧurułej€", "←ðßðæßđæßæđßŋŋæ @~~·ŋŋ·¶·ŋ“¶¬@@")
        self.assertRaises(ValueError, expression_to_dot, e)

    def test_dot_stress(self):
        seed("I have come here to chew bubblegum and kick ass... "
             "and I'm all out of bubblegum.")
        dot_file = tempfile.NamedTemporaryFile()
        cmdline = "dot %s" % dot_file.name
        msg = "dot returned error code {}, check {} input file."
        for _ in xrange(100):
            expression = random_expression()
            _, dot_string = expression_to_dot(expression)
            with open(dot_file.name, "w") as filehandler:
                filehandler.write(dot_string.encode("utf-8"))

            try:
                retcode = subprocess.call(cmdline.split(),
                                          stdout=tempfile.TemporaryFile())
            except OSError:
                print "Warning: the program 'dot' was not found, tests skipped"
                return
            if retcode != 0:
                dot_file.delete = False
            self.assertEqual(retcode, 0, msg.format(retcode, dot_file.name))


if __name__ == "__main__":
    unittest.main()
