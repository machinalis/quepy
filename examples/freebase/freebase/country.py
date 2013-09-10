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

from dsl import *
from refo import Plus, Question
from quepy.dsl import HasKeyword
from quepy.parsing import Lemma, Pos, QuestionTemplate, Token, Particle


class Country(Particle):
    regex = Plus(Pos("DT") | Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS"))

    def interpret(self, match):
        name = match.words.tokens.title()
        return IsCountry() + HasKeyword(name)


class PresidentOfQuestion(QuestionTemplate):
    """
    Ex: "list presidents of Argentina?"
    """

    regex = Question(Lemma("list")) + Lemma("president") + Pos("IN") + \
            Country() + Question(Pos("."))

    def interpret(self, match):
        president = IsPresident() + PresidentOf(match.country)
        name = NameOf(OfficeHolderOf(president))
        return name


class CapitalOfQuestion(QuestionTemplate):
    """
    Regex for questions about the capital of a country.
    Ex: "What is the capital of Bolivia?"
    """

    opening = Lemma("what") + Token("is")
    regex = opening + Pos("DT") + Lemma("capital") + Pos("IN") + \
        Question(Pos("DT")) + Country() + Question(Pos("."))

    def interpret(self, match):
        capital = CapitalOf(match.country)
        label = NameOf(capital)
        return label


class LanguageOfQuestion(QuestionTemplate):
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

    def interpret(self, match):
        language = LanguageOf(match.country)
        name = NameOf(language)
        return name


class PopulationOfQuestion(QuestionTemplate):
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

    def interpret(self, match):
        population = NumberOf(PopulationOf(match.country))
        return population
