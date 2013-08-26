# -*- coding: utf-8 -*-

"""
Sparql generation code.
"""

from quepy import settings
from quepy.expression import isnode
from quepy.semantics import IsRelatedTo
from quepy.encodingpolicy import assert_valid_encoding

_indent = u"  "


def adapt(x):
    if isnode(x):
        x = u"?x{}".format(x)
        return x
    if isinstance(x, basestring):
        assert_valid_encoding(x)
        if x.startswith(u"\""):
            return x
        return u'"{}"'.format(x)
    return unicode(x)


def expression_to_sparql(e, full=False):
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


def triple(a, p, b, indentation=0):
    s = _indent * indentation + u"{0} {1} {2}."
    return s.format(a, p, b)
