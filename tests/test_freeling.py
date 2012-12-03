#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Freeling tests.
"""

import unittest
from StringIO import StringIO

from quepy import sysutils
from quepy import freeling


FREELING_CMD = None  # Complete this to run the tests
assert FREELING_CMD is not None, "Complete the freeling command to run the tests"


class TestFreeling(unittest.TestCase):
    def test_run_freeling(self):

        class FakeStringIO(StringIO):
            name = "some_name"

        class FakeExecutionCtx(object):
            runcmd_called = False

            def __init__(self, *args, **kwargs):
                pass

            def runcmd(self, cmd, stdin=None):
                self.cmd = cmd
                FakeExecutionCtx.runcmd_called = True
                return (StringIO(), StringIO())

            def tmpfile(self, name):
                return FakeStringIO()

        class FakeFunction(object):
            def __init__(self):
                self.called = False
                self.args = None
                self.kwargs = None

            def __call__(self, *args, **kwargs):
                self.called = True
                self.args = args
                self.kwargs = kwargs

        bkp_ctx = sysutils.ExecutionContext
        bkp_parse_output = freeling._parse_freeling_output

        sysutils.ExecutionContext = FakeExecutionCtx
        fake_parse_output = FakeFunction()
        freeling._parse_freeling_output = fake_parse_output

        freeling.run_freeling(u"who is Tom Cruise?", FREELING_CMD)

        self.assertTrue(FakeExecutionCtx.runcmd_called)
        self.assertTrue(fake_parse_output.called)

        sysutils.ExecutionContext = bkp_ctx
        freeling._parse_freeling_output = bkp_parse_output

    def test_real_run(self):
        out = freeling.run_freeling(u"who is Tom Cruise?", FREELING_CMD)
        out = list(out)

        expected_pos = {
            u"who": u"WP",
            u"is": u"VBZ",
            u"Tom Cruise": u"NNP",
            u"?": u".",
        }

        for word in out:
            self.assertIsInstance(word, freeling.Word)
            self.assertEqual(word.pos, expected_pos[word.token])

    def __test_tokens(self, phrase, expected_tokens):
        out = freeling.get_tokens(phrase.decode("utf-8"), FREELING_CMD)

        for token in out:
            self.assertIsInstance(token, unicode)

        self.assertEqual(out, expected_tokens)

    def test_tokens(self):
        self.__test_tokens(u"what is the answer to the ultimate question "
                           u"of life, the universe, and everything",
                           [u"what", u"is", u"the", u"answer", u"to", u"the",
                            u"ultimate", u"question", u"of", u"life", u",",
                            u"the", u"universe", u",", u"and", u"everything"])

    def test_tokens_with_spaces(self):
        self.__test_tokens(u"what is function(param, param2,   param)",
                           [u"what", u"is", u"function(param, param2,   param)"])

    def test_tokens_dotted(self):
        self.__test_tokens(u"what is urllib.urlopen?",
                           [u"what", u"is", u"urllib.urlopen", u"?"])

        self.__test_tokens(u"what is os.path.isdir?",
                           [u"what", u"is", u"os.path.isdir", u"?"])

        self.__test_tokens(u"what is os.path.isdir()?",
                           [u"what", u"is", u"os.path.isdir()", u"?"])

    def test_tokens_underscore(self):
        self.__test_tokens(u"what is urllib.__class__()?",
                           [u"what", u"is", u"urllib.__class__()", u"?"])


if __name__ == "__main__":
    unittest.main()
