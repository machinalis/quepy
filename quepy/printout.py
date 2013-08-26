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

import random
import logging

from quepy.expression import isnode
from quepy.semantics import IsRelatedTo, HasKeyword
from quepy.encodingpolicy import assert_valid_encoding

_indent = u"  "


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
    d = {u"rdf:type": dot_type,
         HasKeyword.relation: dot_keyword,
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
    template = u"{preamble}\n" +\
               u"SELECT DISTINCT {select} WHERE {{\n" +\
               u"    {expression}\n" +\
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
