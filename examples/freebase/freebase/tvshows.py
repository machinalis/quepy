# coding: utf-8

"""
Tv Shows related regex.
"""

from dsl import *
from refo import Plus, Question
from quepy.dsl import HasKeyword
from quepy.parsing import Lemma, Lemmas, Pos, QuestionTemplate, Particle

nouns = Plus(Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS"))


class TvShow(Particle):
    regex = Plus(Question(Pos("DT")) + nouns)

    def interpret(self, match):
        name = match.words.tokens
        return IsTvShow() + HasName(name)


class Actor(Particle):
    regex = nouns

    def interpret(self, match):
        name = match.words.tokens
        return IsPerson() + HasName(name)


class CastOfQuestion(QuestionTemplate):
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

    def interpret(self, match):
        cast = CastOf(match.tvshow)
        actor = IsPerson() + IsActorOf(cast)
        name = NameOf(actor)
        return name


class ListTvShows(QuestionTemplate):
    """
    Ex: "List TV shows"
    """

    regex = Lemmas("list tv show")

    def interpret(self, match):
        show = IsTvShow()
        label = NameOf(show)
        return label


class EpisodeCountQuestion(QuestionTemplate):
    """
    Ex: "How many episodes does Seinfeld have?"
        "Number of episodes of Seinfeld"
    """

    regex = ((Lemmas("how many episode do") + TvShow() + Lemma("have")) |
             (Lemma("number") + Pos("IN") + Lemma("episode") +
              Pos("IN") + TvShow())) + \
            Question(Pos("."))

    def interpret(self, match):
        number_of_episodes = NumberOfEpisodesIn(match.tvshow)
        return number_of_episodes


class ShowsWithQuestion(QuestionTemplate):
    """
    Ex: "List shows with Hugh Laurie"
        "In what shows does Jennifer Aniston appears?"
        "Shows with Matt LeBlanc"
    """

    regex = (Lemmas("list show") + Pos("IN") + Actor()) | \
            (Pos("IN") + (Lemma("what") | Lemma("which")) + Lemmas("show do") +
             Actor() + (Lemma("appear") | Lemma("work")) +
             Question(Pos("."))) | \
            ((Lemma("show") | Lemma("shows")) + Pos("IN") + Actor())

    def interpret(self, match):
        cast = HasActor(match.actor)
        show = IsTvShow() + HasCast(cast)
        show_name = NameOf(show)
        return show_name


class CreatorOfQuestion(QuestionTemplate):
    """
    Ex: "Who is the creator of Breaking Bad?"
        "Who are the creators of Friends?"
    """

    regex = Question(Lemmas("who be") + Pos("DT")) + \
        Lemma("creator") + Pos("IN") + TvShow() + Question(Pos("."))

    def interpret(self, match):
        creator = CreatorOf(match.tvshow)
        name = NameOf(creator)
        return name
