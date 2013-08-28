# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Prasing for freebase app.
"""

from refo import Question
from dsl import DefinitionOf
from quepy.dsl import HasKeyword
from quepy.parsing import RegexTemplate, Particle, Lemma, Pos

from music import *
from people import *
from movies import *


class Thing(Particle):
    regex = Question(Pos("JJ")) + (Pos("NN") | Pos("NNP") | Pos("NNS")) |\
            Pos("VBN")

    def interpret(self, match):
        return HasKeyword(match.words.tokens)


class WhatIs(RegexTemplate):
    """
    Regex for questions like "What is a blowtorch
    Ex: "What is a car"
        "What is Seinfield?"
    """

    regex = Lemma("what") + Lemma("be") + Question(Pos("DT")) + \
        Thing() + Question(Pos("."))

    def interpret(self, match):
        label = DefinitionOf(match.thing)
        return label, "define"
