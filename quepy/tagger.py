#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

import logging
from quepy import settings
from quepy.encodingpolicy import assert_valid_encoding

logger = logging.getLogger("quepy.tagger")
PENN_TAGSET = set(u"$ `` '' ( ) , -- . : CC CD DT EX FW IN JJ JJR JJS LS MD "
                  "NN NNP NNPS NNS PDT POS PRP PRP$ RB RBR RBS RP SYM TO UH "
                  "VB VBD VBG VBN VBP VBZ WDT WP WP$ WRB".split())


class TaggingError(Exception):
    """
    Error parsing tagger's output.
    """
    pass


class Word(object):
    """
    Representation of a tagged word.
    Contains *token*, *lemma*, *pos tag* and optionally a *probability* of
    that tag.
    """

    _encoding_attrs = u"token lemma pos".split()
    _attrs = _encoding_attrs + [u"prob"]
    _fmt = u" ".join(u"{:13.13}" for _ in _attrs)

    def __init__(self, token, lemma=None, pos=None, prob=None):
        self.pos = pos
        self.prob = prob
        self.lemma = lemma
        self.token = token

    def __setattr__(self, name, value):
        if name in self._encoding_attrs and value is not None:
            assert_valid_encoding(value)
        object.__setattr__(self, name, value)

    def fullstr(self):
        """
        Returns a full string representation of the Word object
        """
        attrs_rep = (repr(getattr(self, name, u"-")) for name in self._attrs)
        return self._fmt.format(*attrs_rep)

    def __unicode__(self):
        return u"{}".format(self.token)

    def __repr__(self):
        return u"{}|{}|{}".format(self.token, self.lemma, self.pos)


def get_tagger():
    """
    Return a tagging function given some app settings.
    `Settings` is the settings module of an app.
    The returned value is a function that receives a unicode string and returns
    a list of `Word` instances.
    """
    if settings.USE_FREELING:
        from quepy.freeling import run_freeling
        tagger_function = lambda x: run_freeling(x, settings.FREELING_CMD)
    else:
        from quepy.nltktagger import run_nltktagger
        tagger_function = lambda x: run_nltktagger(x, settings.NLTK_DATA_PATH)

    def wrapper(string):
        assert_valid_encoding(string)
        words = tagger_function(string)
        for word in words:
            if word.pos not in PENN_TAGSET:
                logger.warning("Tagger emmited a non-penn "
                               "POS tag {!r}".format(word.pos))
        return words
    return wrapper
