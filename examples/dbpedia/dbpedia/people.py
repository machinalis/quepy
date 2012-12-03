#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
People related regex
"""


from refo import Plus, Question
from quepy.regex import Lemma, Lemmas, Pos, RegexTemplate, Particle
from quepy.semantics import HasKeyword
from semantics import IsPerson, LabelOf, DefinitionOf, \
                      BirthDateOf, BirthPlaceOf


class Person(Particle):
    regex = Plus(Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS"))

    def semantics(self, match):
        name = match.words.tokens
        return IsPerson() + HasKeyword(name)


class WhoIs(RegexTemplate):
    """
    Ex: "Who is Tom Cruise?"
    """

    regex = Lemma("who") + Lemma("be") + Person() + \
        Question(Pos("."))

    def semantics(self, match):
        definition = DefinitionOf(match.person)
        return definition, "define"


class HowOldIsRegex(RegexTemplate):
    """
    Ex: "How old is Bob Dylan".
    """

    regex = Pos("WRB") + Lemma("old") + Lemma("be") + Person() + \
        Question(Pos("."))

    def semantics(self, match):
        birth_date = BirthDateOf(match.person)
        return birth_date, "age"


class WhereIsFromRegex(RegexTemplate):
    """
    Ex: "Where is Bill Gates from?"
    """

    regex = Lemmas("where be") + Person() + Lemma("from") + \
        Question(Pos("."))

    def semantics(self, match):
        birth_place = BirthPlaceOf(match.person)
        label = LabelOf(birth_place)

        return label, "enum"
