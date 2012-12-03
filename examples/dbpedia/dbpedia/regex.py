#!/usr/bin/env python

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>
# coding: utf-8

"""
Regex for DBpedia quepy.
"""

from refo import Group, Plus, Question
from quepy.semantics import HasKeyword, IsRelatedTo, HasType
from quepy.semantic_utils import handle_noun_phrase
from quepy.regex import Lemma, Pos, RegexTemplate, Token
from semantics import DefinitionOf, LabelOf, IsPlace, UTCof


# Import all the specific type related regex
from music import *
from movies import *
from people import *
from country import *
from tvshows import *
from writers import *


# Openings
LISTOPEN = Lemma("list") | Lemma("name")


class WhatIs(RegexTemplate):
    """
    Regex for questions like "What is ..."
    Ex: "What is a car"
    """

    target = Group(Question(Pos("JJ")) + Pos("NN"), "target")
    regex = Lemma("what") + Lemma("be") + Question(Pos("DT")) + \
        target + Question(Pos("."))

    def semantics(self, match):
        target = handle_noun_phrase(match.target)
        label = DefinitionOf(target)

        return label, "define"


class ListEntity(RegexTemplate):
    """
    Regex for questions like "List ..."
    Ex: "List Microsoft software"
    """

    entity = Group(Pos("NNP"), "entity")
    target = Group(Pos("NN") | Pos("NNS"), "target")
    regex = LISTOPEN + entity + target

    def semantics(self, match):
        entity = HasKeyword(match.entity.tokens)
        target_type = HasKeyword(match.target.lemmas)
        target = HasType(target_type) + IsRelatedTo(entity)
        label = LabelOf(target)

        return label, "enum"


class WhatTimeIs(RegexTemplate):
    """
    Regex for questions about the time
    Ex: "What time is in Cordoba"
    """

    nouns = Plus(Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS"))
    place = Group(nouns, "place")
    openings = (Lemma("what") + Lemma("time") + Token("is")) | Lemma("time")
    regex = openings + Pos("IN") + place + Question(Pos("."))

    def semantics(self, match):
        place = HasKeyword(match.place.lemmas.title()) + IsPlace()
        utc_offset = UTCof(place)

        return utc_offset, "time"
