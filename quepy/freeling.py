#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Provides an interface to run freeling on sentences.
"""

import os
import re

from quepy import sysutils
from quepy.tagger import TaggingError, Word
from quepy.encodingpolicy import assert_valid_encoding

LANG_DIR = os.path.join(os.path.dirname(__file__), "languages")
FREELING_FUNCTION_OUTPUT_REGEX = re.compile(".+?\((.*?)\s*,*\s*\)")


def run_freeling(string, freeling_cmd):
    """
    Runs freeling on `string` and returns a list of Word objects.
    """
    assert_valid_encoding(string)

    ctx = sysutils.ExecutionContext()
    base_path = os.path.join(os.path.dirname(__file__), "freeling_data")
    config_path = __get_config_path(base_path)

    cmdline = freeling_cmd + \
        " -f {0} --train".format(config_path)
    stdin = ctx.tmpfile("freeling_input")
    stdin.write(string.encode("utf-8"))
    stdin.seek(0)
    stdout, _ = ctx.runcmd(cmdline, stdin=stdin)
    stdout.seek(0)
    return _parse_freeling_output(stdout)


def get_tokens(string, freeling_cmd):
    """
    Runs freeling on `string` and returns a list of tokens.
    """

    freeling_out = run_freeling(string, freeling_cmd)
    tokens = []
    for word in freeling_out:
        if not word:
            continue

        tokens.append(word.token)

    return tokens


def __get_config_path(base_path):
    """
    Returns the config filepath after all the replacements.
    """

    ctx = sysutils.ExecutionContext(delete=False)
    template_path = os.path.join(base_path, "freeling.cfg")
    config_file = ctx.tmpfile("freeling")

    template_replacements = {
        "locutions": os.path.join(os.path.abspath(base_path), "locutions.dat"),
        "tokenizer": os.path.join(os.path.abspath(base_path), "tokenizer.dat"),
    }

    with open(template_path) as filehandler:
        template_data = filehandler.read()

    for key in template_replacements:
        template_data = template_data.replace("{%s}" % key,
                                              template_replacements[key])

    config_file.write(template_data)
    return config_file.name


def _read_line(text):
    """
    Parses a line of the freeling command line output.
    """

    assert_valid_encoding(text)
    assert u"#" in text

    start, text = text.split(u"#", 1)

    start = start.strip().rsplit(u" ", 1)[0]
    text = text.strip()
    token_has_spaces = False

    if start.count(u" ") > 2:
        token = FREELING_FUNCTION_OUTPUT_REGEX.match(start)
        assert not token is None
        token = token.group()
        token_has_spaces = True
    else:
        token = start.split(u" ")[0]

    if token_has_spaces:
        text = text.replace(token, u"<token>")

    text = text.split(u" ")
    assert len(text) % 4 == 0

    best_word = None
    while text:
        word = Word(token)
        word.sense = text.pop()
        try:
            word.prob = float(text.pop())
        except ValueError:
            raise TaggingError(u"The probability field of a"
                               u" word was non-numerical")
        if word.prob < 0 or word.prob > 1:
            raise TaggingError(u"The probability field of a"
                               u" word was not a probability")

        word.pos = text.pop()
        word.lemma = text.pop()

        if word.pos in (u"NNP", u"MR"):
            word.token = word.token.replace(u"_", u" ")

        if word.token == u"?" and word.pos == u"Fit":
            word.pos = u"."

        if not best_word or word.prob > best_word.prob:
            best_word = word

    return best_word


def _parse_freeling_output(fin):
    """
    Parses the freeling command line output.
    """

    words = []
    for line in fin:
        line = line.strip()
        if line:
            # FIXME: Decoding from ascii, but we should check what
            # does freeling really writes
            line = line.decode("ascii")
            words.append(_read_line(line))

    return words


if __name__ == "__main__":
    import sys

    freeling_out = run_freeling(" ".join(sys.argv[2:]).decode("utf-8"),
                                sys.argv[1])

    attrs = "TOKEN LEMMA POS PROB SENSE".split()
    print " ".join(["{:13.13}".format(x) for x in attrs])

    for word in freeling_out:
        print word.fullstr()
