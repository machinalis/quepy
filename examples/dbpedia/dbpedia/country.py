#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Coutry related regex
"""

from refo import Plus, Question
from quepy.semantics import HasKeyword
from quepy.regex import Lemma, Pos, RegexTemplate, Token, Particle
from semantics import IsCountry, IncumbentOf, CapitalOf, LabelOf, \
                      LanguageOf, PopulationOf, PresidentOf


class Country(Particle):
    regex = Plus(Pos("NN") | Pos("NNP"))

    def semantics(self, match):
        name = match.words.tokens.title()
        return IsCountry() + HasKeyword(name)


class PresidentOfRegex(RegexTemplate):
    """
    Regex for questions about the president of a country.
    Ex: "Who is the president of Argentina?"
    """

    regex = Lemma("who") + Token("is") + Pos("DT") + Lemma("president") + \
        Pos("IN") + Country() + Question(Pos("."))

    def semantics(self, match):
        president = PresidentOf(match.country)
        incumbent = IncumbentOf(president)
        label = LabelOf(incumbent)

        return label, "enum"


class CapitalOfRegex(RegexTemplate):
    """
    Regex for questions about the capital of a country.
    Ex: "What is the capital of Bolivia?"
    """

    opening = Lemma("what") + Token("is")
    regex = opening + Pos("DT") + Lemma("capital") + Pos("IN") + \
        Question(Pos("DT")) + Country() + Question(Pos("."))

    def semantics(self, match):
        capital = CapitalOf(match.country)
        label = LabelOf(capital)
        return label, "enum"


# FIXME: the generated query needs FILTER isLiteral() to the head
# because dbpedia sometimes returns different things
class LanguageOfRegex(RegexTemplate):
    """
    Regex for questions about the language spoken in a country.
    Ex: "What is the language of Argentina?"
        "what language is spoken in Argentina?"
    """

    openings = (Lemma("what") + Token("is") + Pos("DT") +
                Question(Lemma("official")) + Lemma("language")) | \
               (Lemma("what") + Lemma("language") + Token("is") +
                Lemma("speak"))

    regex = openings + Pos("IN") + Question(Pos("DT")) + Country() + \
        Question(Pos("."))

    def semantics(self, match):
        language = LanguageOf(match.country)
        return language, "enum"


class PopulationOfRegex(RegexTemplate):
    """
    Regex for questions about the population of a country.
    Ex: "What is the population of China?"
        "How many people live in China?"
    """

    openings = (Pos("WP") + Token("is") + Pos("DT") +
                Lemma("population") + Pos("IN")) | \
               (Pos("WRB") + Lemma("many") + Lemma("people") +
                Token("live") + Pos("IN"))
    regex = openings + Question(Pos("DT")) + Country() + Question(Pos("."))

    def semantics(self, match):
        population = PopulationOf(match.country)
        return population, "literal"
