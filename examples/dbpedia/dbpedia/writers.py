# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Writers related regex.
"""


from refo import Plus, Question
from quepy.dsl import HasKeyword
from quepy.parsing import Lemma, Lemmas, Pos, QuestionTemplate, Particle
from dsl import IsBook, HasAuthor, AuthorOf, IsPerson, NameOf


nouns = Pos("DT") | Pos("IN") | Pos("NN") | Pos("NNS") | Pos("NNP") | Pos("NNPS")


class Book(Particle):
    regex = Plus(nouns)

    def interpret(self, match):
        name = match.words.tokens
        return IsBook() + HasKeyword(name)


class Author(Particle):
    regex = Plus(nouns | Lemma("."))

    def interpret(self, match):
        name = match.words.tokens
        return IsPerson() + HasKeyword(name)


class WhoWroteQuestion(QuestionTemplate):
    """
    Ex: "who wrote The Little Prince?"
        "who is the author of A Game Of Thrones?"
    """

    regex = ((Lemmas("who write") + Book()) |
             (Question(Lemmas("who be") + Pos("DT")) +
              Lemma("author") + Pos("IN") + Book())) + \
            Question(Pos("."))

    def interpret(self, match):
        author = NameOf(IsPerson() + AuthorOf(match.book))
        return author, "literal"


class BooksByAuthorQuestion(QuestionTemplate):
    """
    Ex: "list books by George Orwell"
        "which books did Suzanne Collins wrote?"
    """

    regex = (Question(Lemma("list")) + Lemmas("book by") + Author()) | \
            ((Lemma("which") | Lemma("what")) + Lemmas("book do") +
             Author() + Lemma("write") + Question(Pos(".")))

    def interpret(self, match):
        book = IsBook() + HasAuthor(match.author)
        book_name = NameOf(book)
        return book_name, "enum"
