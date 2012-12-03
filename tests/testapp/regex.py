#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Regex for testapp quepy.
"""

from quepy.regex import RegexTemplate, Token
from quepy.semantics import HasKeyword
from refo import Star, Any


class LowMatchAny(RegexTemplate):
    weight = 0.5
    regex = Star(Any())

    def semantics(self, match):
        expr = None

        for word in match.words:
            if expr is not None:
                expr += HasKeyword(word.token)
            else:
                expr = HasKeyword(word.token)

        return expr


class MatchAny(LowMatchAny):
    weight = 0.8

    def semantics(self, match):
        expr = super(MatchAny, self).semantics(match)
        return expr, 42


class UserData(RegexTemplate):
    weight = 1.0
    regex = Token("user") + Token("data")

    def semantics(self, match):
        return HasKeyword(match.words[0].token), "<user data>"
