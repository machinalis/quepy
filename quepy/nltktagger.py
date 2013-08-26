# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Tagging using NLTK.
"""

# Requiered data files are:
#   - "maxent_treebank_pos_tagger" in Models
#   - "wordnet" in Corpora

import nltk
from quepy.tagger import Word
from quepy.encodingpolicy import assert_valid_encoding

_penn_to_morphy_tag = {}


def penn_to_morphy_tag(tag):
    assert_valid_encoding(tag)

    for penn, morphy in _penn_to_morphy_tag.iteritems():
        if tag.startswith(penn):
            return morphy
    return None


def run_nltktagger(string, nltk_data_path=None):
    """
    Runs nltk tagger on `string` and returns a list of
    :class:`quepy.tagger.Word` objects.
    """
    assert_valid_encoding(string)
    global _penn_to_morphy_tag

    if nltk_data_path:
        nltk.data.path = nltk_data_path

    from nltk.corpus import wordnet

    if not _penn_to_morphy_tag:
        _penn_to_morphy_tag = {
            u'NN': wordnet.NOUN,
            u'JJ': wordnet.ADJ,
            u'VB': wordnet.VERB,
            u'RB': wordnet.ADV,
        }

    # Recommended tokenizer doesn't handle non-ascii characters very well
    #tokens = nltk.word_tokenize(string)
    tokens = nltk.wordpunct_tokenize(string)
    tags = nltk.pos_tag(tokens)

    words = []
    for token, pos in tags:
        word = Word(token)
        # Eliminates stuff like JJ|CC
        # decode ascii because they are the penn-like POS tags (are ascii).
        word.pos = pos.split("|")[0].decode("ascii")

        mtag = penn_to_morphy_tag(word.pos)
        # Nice shooting, son. What's your name?
        lemma = wordnet.morphy(word.token, pos=mtag)
        if isinstance(lemma, str):
            # In this case lemma is example-based, because if it's rule based
            # the result should be unicode (input was unicode).
            # Since english is ascii the decoding is ok.
            lemma = lemma.decode("ascii")
        word.lemma = lemma
        if word.lemma is None:
            word.lemma = word.token.lower()

        words.append(word)

    return words
