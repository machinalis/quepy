#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Helper functions to handle semantics.
"""

import random
from quepy.encodingpolicy import assert_valid_encoding


_indent = u"  "


class BadSemantic(Exception):
    """
    Problem with the semantic.
    """


class RegexSemanticFailed(Exception):
    pass


class UnhandledWord(RegexSemanticFailed):
    pass


class BadNounLike(RegexSemanticFailed):
    pass


def handle_keywords(text, split=True):
    """
    Automatic handling of Keywords from a text.
    It runs the sanitize function for keywords on every
    keyword.

    If `split` it's True, it splits the text by white spaces.

    Returns an :class:`quepy.expression.Expression` that represents
    the fact of having the keywords extracted from text.
    """

    assert_valid_encoding(text)

    from quepy.semantics import HasKeyword

    if split:
        keywords = [HasKeyword.sanitize(x) for x in text.split()]
    else:
        keywords = (HasKeyword.sanitize(text),)

    if not keywords:
        raise ValueError(u"Couldn't extract any keyword from '%s'" % text)

    expr = None
    for keyword in keywords:
        if expr is not None:
            expr += HasKeyword(keyword)
        else:
            expr = HasKeyword(keyword)

    return expr


def handle_nounlike(word):
    """
    Handles things that might be a noun or a special
    thing like a Handler.

    Returns an :class:`quepy.expression.Expression`.
    """

    from quepy import handlers
    from quepy.semantics import HasKeyword

    handler = handlers.get_handler(word)

    if handler:
        return handler(word)
    elif word.pos in (u"NN", u"NP", u"NNP", u"NNS"):
        return HasKeyword(word.lemma)
    else:
        raise UnhandledWord(u"Couldn't handle word {0!r}".format(word))


def handle_noun_phrase(words, flatten=False, ignore_jj=False):
    # FIXME: doc

    from quepy.semantics import HasKeyword, IsRelatedTo
    if not words:
        raise BadNounLike(u"{0!r} is not noun-phrase-like".format(words))

    head = handle_nounlike(words.pop())
    xs = [head]
    while words:
        word = words.pop()
        if word.pos == u"JJ" and not ignore_jj:
            head += HasKeyword(word.lemma)
        else:
            head = handle_nounlike(word)
            xs.append(head)
    if flatten:
        head = xs.pop()
        for x in xs:
            head += x
    else:
        head = xs.pop()
        while xs:
            head = xs.pop() + IsRelatedTo(head)

    return head


def try_handler(self, word):
    """
    Tries to use a :class:`quepy.handlers.Handler` on word
    and returns the semantic associated or None otherwise.
    """

    from quepy import handlers

    handler = handlers.get_handler(word)

    if handler:
        return handler(word)


def easy_regex_map(regex, string):
    xs = []
    for s in string.split():
        xs.append(regex(s))
    assert xs
    if len(xs) == 1:
        return xs[0]
    x = xs[0]
    for y in xs[1:]:
        x += y
    return x


def _symmetric_and_reflexive(d):
    it = d.items()
    for var, s in it:
        #symmetric
        for other in s:
            t = d.get(other, set())
            t.add(var)
            d[other] = t
    for var, s in d.iteritems():
        #reflexive
        s.add(var)


def _connected_to(start, d):
    q = [start]
    c = set(q)
    while q:
        var = q.pop()
        assert var.resolve_binding() is var
        for other in d.get(var, []):
            if not other in c:
                c.add(other)
                q.append(other)
    return c


def triple(a, p, b, indentation=0):
    s = _indent * indentation + u"{0} {1} {2}."
    return s.format(a, p, b)


def dot_arc(a, label, b):
    assert u" " not in a and u" " not in b
    return u"{0} -> {1} [label=\"{2}\"];".format(a, b, label)


def dot_type(a, t):
    s = u"{0} [shape=box];\n".format(t)
    return s + u"{0} -> {1} [color=red, arrowhead=empty];".format(a, t)


def dot_attribute(a, key):
    blank = id(a)
    s = u"{0} [shape=none label={1}];\n".format(blank, key)
    return s + u"{0} -> {1};".format(a, blank)


def dot_keyword(a, key):
    blank = u"{0:.30f}".format(random.random())
    blank = u"blank" + blank.replace(u".", u"")
    s = u"{0} [shape=none label={1}];\n".format(blank, key)
    return s + u"{0} -> {1} [style=dashed];".format(a, blank)


def dot_fixed_type(a, fixedtype):
    blank = u"{0:.30f}".format(random.random())
    blank = u"blank" + blank.replace(u".", u"")
    s = u"{0} [shape=box label={1}];\n".format(blank, fixedtype)
    return s + u"{0} -> {1} [color=red, arrowhead=empty];".format(a, blank)
