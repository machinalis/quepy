# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Basic questions for Freebase.
"""

from refo import Question, Plus
from dsl import DefinitionOf, NameOf, LocationOf
from quepy.dsl import HasKeyword
from quepy.parsing import QuestionTemplate, Particle, Lemma, Pos, Lemmas


class Thing(Particle):
    regex = Plus(Question(Pos("JJ")) + (Pos("NN") | Pos("NNP") | Pos("NNS")) |
            Pos("VBN"))

    def interpret(self, match):
        return HasKeyword(match.words.tokens)


class WhatIs(QuestionTemplate):
    """
    Regex for questions like "What is a blowtorch
    Ex: "What is a car"
        "What is Seinfield?"
    """

    regex = Lemma("what") + Lemma("be") + Question(Pos("DT")) + \
        Thing() + Question(Pos("."))

    def interpret(self, match):
        label = DefinitionOf(match.thing)
        return label


class WhereIsQuestion(QuestionTemplate):
    """
    Ex: "where in the world is the Eiffel Tower"
    """

    regex = Lemma("where") + Question(Lemmas("in the world")) + Lemma("be") + \
        Question(Pos("DT")) + Thing() + Question(Pos("."))

    def interpret(self, match):
        location = LocationOf(match.thing)
        location_name = NameOf(location)
        return location_name
