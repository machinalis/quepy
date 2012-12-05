#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Movie related regex.
"""

from refo import Plus, Question
from quepy.semantics import HasKeyword
from quepy.regex import Lemma, Lemmas, Pos, RegexTemplate, Particle
from semantics import IsMovie, NameOf, IsPerson, DirectedBy, LabelOf, \
                      DurationOf, HasActor, HasName, ReleaseDateOf, \
                      DirectorOf, StarsIn, DefinitionOf

nouns = Plus(Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS"))


class Movie(Particle):
    regex = Question(Pos("DT")) + nouns

    def semantics(self, match):
        name = match.words.tokens
        return IsMovie() + HasName(name)


class Actor(Particle):
    regex = nouns

    def semantics(self, match):
        name = match.words.tokens
        return IsPerson() + HasKeyword(name)


class Director(Particle):
    regex = nouns

    def semantics(self, match):
        name = match.words.tokens
        return IsPerson() + HasKeyword(name)


class ListMoviesRegex(RegexTemplate):
    """
    Ex: "list movies"
    """

    regex = Lemma("list") + (Lemma("movie") | Lemma("film"))

    def semantics(self, match):
        movie = IsMovie()
        name = NameOf(movie)
        return name, "enum"


class MoviesByDirectorRegex(RegexTemplate):
    """
    Ex: "List movies by Quentin Tarantino.
        "movies directed by Martin Scorsese"
        "which movies did Mel Gibson directed"
    """

    regex = (Question(Lemma("list")) + (Lemma("movie") | Lemma("film")) +
             Question(Lemma("direct")) + Lemma("by") + Director()) | \
            (Lemma("which") + (Lemma("movie") | Lemma("film")) + Lemma("do") +
             Director() + Lemma("direct") + Question(Pos(".")))

    def semantics(self, match):
        movie = IsMovie() + DirectedBy(match.director)
        movie_name = LabelOf(movie)

        return movie_name, "enum"


class MovieDurationRegex(RegexTemplate):
    """
    Ex: "How long is Pulp Fiction"
        "What is the duration of The Thin Red Line?"
    """

    regex = ((Lemmas("how long be") + Movie()) |
            (Lemmas("what be") + Pos("DT") + Lemma("duration") +
             Pos("IN") + Movie())) + \
            Question(Pos("."))

    def semantics(self, match):
        duration = DurationOf(match.movie)
        return duration, ("literal", "{} minutes long")


class ActedOnRegex(RegexTemplate):
    """
    Ex: "List movies with Hugh Laurie"
        "Movies with Matt LeBlanc"
        "In what movies did Jennifer Aniston appear?"
        "Which movies did Mel Gibson starred?"
        "Movies starring Winona Ryder"
    """

    acted_on = (Lemma("appear") | Lemma("act") | Lemma("star"))
    movie = (Lemma("movie") | Lemma("film"))
    regex = (Question(Lemma("list")) + movie + Lemma("with") + Actor()) | \
            (Question(Pos("IN")) + (Lemma("what") | Lemma("which")) +
             movie + Lemma("do") + Actor() + acted_on + Question(Pos("."))) | \
            (Question(Pos("IN")) + Lemma("which") + movie + Lemma("do") +
             Actor() + acted_on) | \
            (Question(Lemma("list")) + movie + Lemma("star") + Actor())

    def semantics(self, match):
        movie = IsMovie() + HasActor(match.actor)
        movie_name = NameOf(movie)
        return movie_name, "enum"


class MovieReleaseDateRegex(RegexTemplate):
    """
    Ex: "When was The Red Thin Line released?"
        "Release date of The Empire Strikes Back"
    """

    regex = ((Lemmas("when be") + Movie() + Lemma("release")) |
            (Lemma("release") + Question(Lemma("date")) +
             Pos("IN") + Movie())) + \
            Question(Pos("."))

    def semantics(self, match):
        release_date = ReleaseDateOf(match.movie)
        return release_date, "literal"


class DirectorOfRegex(RegexTemplate):
    """
    Ex: "Who is the director of Big Fish?"
        "who directed Pocahontas?"
    """

    regex = ((Lemmas("who be") + Pos("DT") + Lemma("director") +
             Pos("IN") + Movie()) |
             (Lemma("who") + Lemma("direct") + Movie())) + \
            Question(Pos("."))

    def semantics(self, match):
        director = IsPerson() + DirectorOf(match.movie)
        director_name = NameOf(director)
        return director_name, "literal"


class ActorsOfRegex(RegexTemplate):
    """
    Ex: "who are the actors of Titanic?"
        "who acted in Alien?"
        "who starred in Depredator?"
        "Actors of Fight Club"
    """

    regex = (Lemma("who") + Question(Lemma("be") + Pos("DT")) +
             (Lemma("act") | Lemma("actor") | Lemma("star")) +
             Pos("IN") + Movie() + Question(Pos("."))) | \
            (Lemma("actor") + Pos("IN") + Movie())

    def semantics(self, match):
        actor = NameOf(IsPerson() + StarsIn(match.movie))
        return actor, "enum"


class PlotOfRegex(RegexTemplate):
    """
    Ex: "what is Shame about?"
        "plot of Titanic"
    """

    regex = (Lemmas("what be") + Movie() +
             Lemma("about") + Question(Pos("."))) | \
            (Lemma("plot") + Pos("IN") + Movie())

    def semantics(self, match):
        definition = DefinitionOf(match.movie)
        return definition, "define"
