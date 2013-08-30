# -*- coding: utf-8 -*-

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

import json
from random import seed
import unittest
from random_expression import random_expression
from quepy.mql_generation import generate_mql


class TestMqlGeneration(unittest.TestCase):
    def test_mql_stress(self):
        for _ in xrange(100):
            seed("playadito vs amanda... 3 foc")
            expression = random_expression()
            target, mql = generate_mql(expression)
            json.loads(mql)


if __name__ == "__main__":
    unittest.main()
