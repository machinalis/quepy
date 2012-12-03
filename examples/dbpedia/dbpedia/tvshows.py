#!/usr/bin/env python
# coding: utf-8

"""
Tv Shows related regex.
"""

from refo import Plus, Question
from quepy.semantics import HasKeyword
from quepy.regex import Lemma, Lemmas, Pos, RegexTemplate, Particle
from semantics import IsTvShow, ReleaseDateOf, IsPerson, StarsIn, LabelOf, \
                      HasShowName, NumberOfEpisodesIn, HasActor, ShowNameOf, \
                      CreatorOf

nouns = Plus(Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS"))


class TvShow(Particle):
    regex = nouns

    def semantics(self, match):
        name = match.words.tokens
        return IsTvShow() + HasShowName(name)


class Actor(Particle):
    regex = nouns

    def semantics(self, match):
        name = match.words.tokens
        return IsPerson() + HasKeyword(name)


# FIXME: clash with movies release regex
class ReleaseDateRegex(RegexTemplate):
    """
    Ex: when was Friends release?
    """

    regex = Lemmas("when be") + TvShow() + Lemma("release") + \
        Question(Pos("."))

    def semantics(self, match):
        release_date = ReleaseDateOf(match.tvshow)
        return release_date, "literal"


class CastOfRegex(RegexTemplate):
    """
    Ex: "What is the cast of Friends?"
        "Who works in Breaking Bad?"
        "List actors of Seinfeld"
    """

    regex = (Question(Lemmas("what be") + Pos("DT")) +
             Lemma("cast") + Pos("IN") + TvShow() + Question(Pos("."))) | \
            (Lemmas("who works") + Pos("IN") + TvShow() +
             Question(Pos("."))) | \
            (Lemmas("list actor") + Pos("IN") + TvShow())

    def semantics(self, match):
        actor = IsPerson() + StarsIn(match.tvshow)
        name = LabelOf(actor)
        return name, "enum"


class ListTvShows(RegexTemplate):
    """
    Ex: "List TV shows"
    """

    regex = Lemmas("list tv show")

    def semantics(self, match):
        show = IsTvShow()
        label = LabelOf(show)
        return label, "enum"


class EpisodeCountRegex(RegexTemplate):
    """
    Ex: "How many episodes does Seinfeld have?"
        "Number of episodes of Seinfeld"
    """

    regex = ((Lemmas("how many episode do") + TvShow() + Lemma("have")) |
             (Lemma("number") + Pos("IN") + Lemma("episode") +
              Pos("IN") + TvShow())) + \
            Question(Pos("."))

    def semantics(self, match):
        number_of_episodes = NumberOfEpisodesIn(match.tvshow)
        return number_of_episodes, "literal"


class ShowsWithRegex(RegexTemplate):
    """
    Ex: "List shows with Hugh Laurie"
        "In what shows does Jennifer Aniston appears?"
        "Shows with Matt LeBlanc"
    """

    regex = (Lemmas("list show") + Pos("IN") + Actor()) | \
            (Pos("IN") + Lemmas("what show do") +
             Actor() + (Lemma("appear") | Lemma("work")) +
             Question(Pos("."))) | \
            ((Lemma("show") | Lemma("shows")) + Pos("IN") + Actor())

    def semantics(self, match):
        show = IsTvShow() + HasActor(match.actor)
        show_name = ShowNameOf(show)
        return show_name, "enum"


class CreatorOfRegex(RegexTemplate):
    """
    Ex: "Who is the creator of Breaking Bad?"
    """

    regex = Question(Lemmas("who be") + Pos("DT")) + \
        Lemma("creator") + Pos("IN") + TvShow() + Question(Pos("."))

    def semantics(self, match):
        creator = CreatorOf(match.tvshow)
        label = LabelOf(creator)
        return label, "enum"
