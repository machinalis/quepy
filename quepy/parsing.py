# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

import refo
import logging
from refo import Predicate, Literal, Star, Any, Group

from quepy.encodingpolicy import encoding_flexible_conversion

_EOL = None
logger = logging.getLogger("quepy.parsing")


class BadSemantic(Exception):
    """
    Problem with the semantic.
    """


class WordList(list):
    """
    A list of words with some utils for the user.
    """

    def __init__(self, words):
        super(WordList, self).__init__(self)
        # Add the words to the list
        self.extend(words)

    @property
    def tokens(self):
        return " ".join([x.token for x in self])

    @property
    def lemmas(self):
        return " ".join([x.lemma for x in self])


class Match(object):
    """
    Holds the matching of the regex.
    """

    def __init__(self, match, words, i=None, j=None):
        assert isinstance(i, type(j))  # Aprox: Both None or both int
        self._match = match
        self._words = words
        self._i = i
        self._j = j
        self._particles = {particle.name: particle for particle in match
                           if isinstance(particle, Particle)}

    @property
    def words(self):
        i, j = self._match.span()  # Should be (0, n)
        if self._i is not None:
            i, j = self._i, self._j
        return WordList(self._words[i:j])

    def __getattr__(self, attr):
        if attr in self._particles:
            particle = self._particles[attr]
            i, j = self._match[particle]
            self._check_valid_indexes(i, j, attr)
            match = Match(self._match, self._words, i, j)
            return particle.interpret(match)

        try:
            i, j = self._match[attr]
        except KeyError:
            message = "'{}' object has no attribute '{}'"
            raise AttributeError(message.format(self.__class__.__name__, attr))
        self._check_valid_indexes(i, j, attr)
        return WordList(self._words[i:j])

    def _check_valid_indexes(self, i, j, attr):
        if self._i is None:
            return
        if i < self._i or self._j <= j:
            message = "'{}' object has no attribute '{}'"
            raise AttributeError(message.format(self.__class__.__name__, attr))


class QuestionTemplate(object):
    """
    Subclass from this to implement a question handler.
    """

    regex = Star(Any())  # Must define when subclassing
    weight = 1  # Redefine this to give different priorities to your regexes.

    def interpret(self, match):
        """
        Returns the intermediate representation of the regex.
        `match` is of type `quepy.regex.Match` and is analogous to a python re
        match. It contains matched groups in the regular expression.

        When implementing a regex one must fill this method.
        """
        raise NotImplementedError()

    def get_interpretation(self, words):
        rulename = self.__class__.__name__
        logger.debug("Trying to match with regex: {}".format(rulename))

        match = refo.match(self.regex + Literal(_EOL), words + [_EOL])

        if not match:
            logger.debug("No match")
            return None, None

        try:
            match = Match(match, words)
            result = self.interpret(match)
        except BadSemantic as error:
            logger.debug(str(error))
            return None, None
        try:
            expression, userdata = result
        except TypeError:
            expression, userdata = result, None

        expression.rule_used = rulename
        return expression, userdata


class Pos(Predicate):
    """
    Predicate to check if a word has an specific *POS* tag.
    """

    def __init__(self, tag):
        tag = encoding_flexible_conversion(tag)
        self.tag = tag
        super(Pos, self).__init__(self._predicate)
        self.arg = tag

    def _predicate(self, word):
        return word != _EOL and self._check(word)

    def _check(self, word):
        return word.pos == self.tag


class Lemma(Pos):
    """
    Predicate to check if a word has an specific *lemma*.
    """

    def _check(self, word):
        return word.lemma == self.tag


class Token(Pos):
    """
    Predicate to check if a word has an specific *token*.
    """

    def _check(self, word):
        return word.token == self.tag


class Particle(Group):
    regex = None

    def __init__(self, name=None):
        if self.regex is None:
            message = "A regex must be defined for {}"
            raise NotImplementedError(message.format(self.__class__.__name__))
        if name is None:
            name = self.__class__.__name__.lower()
        self.name = name
        super(Particle, self).__init__(self.regex, self)

    def interpret(self, match):
        message = "A interpretation must be defined for {}"
        raise NotImplementedError(message.format(self.__class__.__name__))

    def __str__(self):
        return repr(self)

    def __repr__(self):
        cname = self.__class__.__name__
        if cname.lower() == self.name:
            return "{}()".format(cname)
        else:
            return "{}('{}')".format(cname, self.name)


def _predicate_sum_from_string(string, predicate):
    assert issubclass(predicate, Predicate)

    string = encoding_flexible_conversion(string)
    words = string.split()
    result = None
    for word in words:
        if result is None:
            result = predicate(word)
        else:
            result += predicate(word)

    return result


def Lemmas(string):
    """
    Returns a Predicate that catches strings
    with the lemmas mentioned on `string`.
    """
    return _predicate_sum_from_string(string, Lemma)


def Tokens(string):
    """
    Returns a Predicate that catches strings
    with the tokens mentioned on `string`.
    """
    return _predicate_sum_from_string(string, Token)


def Poss(string):
    """
    Returns a Predicate that catches strings
    with the POS mentioned on `string`.
    """
    return _predicate_sum_from_string(string, Pos)
