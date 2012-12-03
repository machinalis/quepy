#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Tests for QuepyApp.
"""

import unittest

import quepy


class TestQuepyApp(unittest.TestCase):

    def setUp(self):
        self.app = quepy.install("testapp")

    def test_get_query_types(self):
        question = "What is this?"
        target, query, userdata = self.app.get_query(question)

        self.assertIsInstance(target, unicode)
        self.assertIsInstance(query, unicode)

    def test_get_user_data(self):
        question = "user data"
        target, query, userdata = self.app.get_query(question)
        self.assertEqual(userdata, "<user data>")

    def test_priority(self):
        question = "something something"
        target, query, userdata = self.app.get_query(question)
        self.assertEqual(userdata, 42)

    def test_config_is_saved(self):
        from quepy import settings
        self.assertIn("testapp", settings.SPARQL_PREAMBLE)


if __name__ == "__main__":
    unittest.main()
