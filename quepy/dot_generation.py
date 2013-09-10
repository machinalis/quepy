# -*- coding: utf-8 -*-

"""
Dot generation code.
"""

import random
from quepy.expression import isnode
from quepy.dsl import IsRelatedTo, HasKeyword
from quepy.encodingpolicy import assert_valid_encoding


def escape(x, add_quotes=True):
    x = unicode(x)
    x = x.replace(u" ", u"_")
    x = x.replace(u"\n", u"")
    x = x.replace(u"\00", u"")
    x = x.replace(u"[", u"")
    x = x.replace(u"]", u"")
    x = x.replace(u"\\", u"")
    if x.count("\""):
        x = x.replace(u"\"", u"\\\"")
        if add_quotes:
            x = u'"' + x + u'"'
    return x


def adapt(x):
    if isnode(x):
        x = u"x{}".format(x)
        return x
    if isinstance(x, basestring):
        assert_valid_encoding(x)
        x = escape(x)
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
            node1 = adapt(node)
            node2 = adapt(other)
            relation = escape(relation, add_quotes=False)

            if relation in d:
                x = d[relation](node1, node2)
            else:
                x = dot_arc(node1, relation, node2)
            xs.append(x)
    return None, s.format(adapt(e.head), u"".join(xs))


def dot_arc(a, label, b):
    assert u" " not in a and u" " not in b
    assert u"\n" not in a + label + b
    return u"{0} -> {1} [label=\"{2}\"];\n".format(a, b, label)


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
