#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Provides a way to add custom handlers for certain words.
"""


from refo import Predicate

__HANDLERS = []


class Handler(Predicate):
    """
    Base of all the handlers.
    """

    def __init__(self):
        """
        It creates the handler.
        """

        super(Handler, self).__init__(self.check)

    def check(self, word):
        """
        A boolean method that returns if the word must be
        handled by this class or not.
        """

        message = u"{0}.check not implemented".format(self.__class__.__name__)
        raise NotImplementedError(message)

    def handler(self, word):
        """
        Returns the semantics of the word treated by this class
        """

        message = u"{0}.handler not implemented".format(self.__class__.__name__)
        raise NotImplementedError(message)


def register(handlerclass):
    """
    Adds a custom handler.
    """

    if not issubclass(handlerclass, Handler):
        message = u"parameter it's not a Handler class"
        raise TypeError(message)

    __HANDLERS.append(handlerclass)


def get_handler(word):
    """
    Given a :class:`quepy.tagger.Word` returns the first handler
    found that the check function it's True.
    """

    for handlerclass in __HANDLERS:
        handlerobj = handlerclass()
        if handlerobj.check(word):
            return handlerobj.handler
