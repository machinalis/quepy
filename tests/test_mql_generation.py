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
    def _get_json(self, query):
        try:
            return json.loads(query)
        except ValueError as e:
            if "Unpaired" in str(e) and "surrogate" in str(e):
                # This is a known issue python's json.
                return None

    def _valid_mql_query(self, query):
        x = self._get_json(query)
        if x is None:
            return
        q = [x]
        while q:
            x = q.pop()
            # Each entry is either a [{...}] or a unicode
            if isinstance(x, list):
                self.assertIsInstance(x[0], dict)
                self.assertEqual(len(x), 1)
                for key, value in x[0].iteritems():
                    self.assertIsInstance(key, unicode)
                    q.append(value)
            else:
                self.assertIsInstance(x, unicode)

    def _valid_target_for_query(self, target, query):
        self.assertIsInstance(target, list)
        for entry in target:
            self.assertIsInstance(entry, unicode)
        x = self._get_json(query)
        if x is None:
            return
        target = list(target)
        while target:
            entry = target.pop(0)
            x = x[0][entry]
        self.assertIsInstance(x, list)
        self.assertEqual(len(x), 1)
        self.assertIsInstance(x[0], dict)
        #self.assertEqual(len(x[0]), 0)  # Too strict?

    def test_mql_stress(self):
        seed("playadito vs amanda... 3 focas")
        for _ in xrange(100):
            expression = random_expression()
            target, mql = generate_mql(expression)
            self._valid_mql_query(mql)
            self._valid_target_for_query(target, mql)

if __name__ == "__main__":
    unittest.main()
