#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Output utilities.
"""

import logging
from semantics import IsRelatedTo
from encodingpolicy import assert_valid_encoding
from expression import isnode


def adapt(x, sparql=True):
    if isnode(x):
        x = u"x{}".format(x)
        if sparql:
            x = u"?" + x
        return x
    if isinstance(x, basestring):
        assert_valid_encoding(x)
        if not sparql:
            x = x.replace(" ", "_")
        if x.startswith(u"\""):
            return x
        return u'"{}"'.format(x)
    return unicode(x)


def expression_to_dot(e):
    from semantic_utils import dot_type, dot_keyword, dot_arc
    d = {u"rdf:type": dot_type,
         u"quepy:Keyword": dot_keyword,
         IsRelatedTo: lambda x, y: dot_arc(x, u"", y)}
    s = u"digraph G {{\n{0} [shape=house];\n{1}\n}}\n"
    xs = []
    for node in e.iter_nodes():
        for relation, other in e.iter_edges(node):
            node1 = adapt(node, False)
            node2 = adapt(other, False)

            if node1.startswith(u'"') or ":" in node1:
                node1 = u'"' + node1.replace(u'"', u'\\"') + u'"'
            if node2.startswith('"') or ":" in node2:
                node2 = u'"' + node2.replace(u'"', u'\\"') + u'"'

            if relation in d:
                x = d[relation](node1, node2)
            else:
                x = dot_arc(node1, relation, node2)
            xs.append(x)
    return s.format(adapt(e.head, False), u"".join(xs))


def expression_to_sparql(e, full=False):
    import settings
    from semantic_utils import triple
    template = u"{preamble}\n" +\
               u"SELECT DISTINCT {select} WHERE {{\n" +\
                   u"{expression}\n" +\
               u"}}\n"
    head = adapt(e.get_head())
    if full:
        select = u"*"
    else:
        select = head
    y = 0
    xs = []
    for node in e.iter_nodes():
        for relation, dest in e.iter_edges(node):
            if relation is IsRelatedTo:
                relation = u"?y{}".format(y)
                y += 1
            xs.append(triple(adapt(node), relation, adapt(dest),
                      indentation=1))
    sparql = template.format(preamble=settings.SPARQL_PREAMBLE,
                             select=select,
                             expression=u"\n".join(xs))
    return select, sparql


def set_loglevel(level=logging.WARNING):
    l = logging.getLogger("quepy")
    l.setLevel(level)


_LOGFORMAT = u"[%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(format=_LOGFORMAT)


set_loglevel(logging.INFO)
