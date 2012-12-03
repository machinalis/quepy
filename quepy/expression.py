#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

from collections import defaultdict
from copy import deepcopy


def isnode(x):
    return isinstance(x, int)


class Expression(object):

    def __init__(self):
        self.nodes = []
        self.head = self.add_node()

    def add_node(self):
        i = len(self.nodes)
        self.nodes.append([])
        return i

    def walk_edge(self, node, relation):
        assert node < len(self.nodes)
        for rel, j in self.nodes[node]:
            if rel == relation:
                return j
        return None

    def get_head(self):
        return self.head

    def merge(self, other):
        """
        Precondition: every expression has only one connected component
        """
        translation = defaultdict(self.add_node)
        translation[other.head] = self.head
        for node in other.iter_nodes():
            for relation, dest in other.iter_edges(node):
                xs = self.nodes[translation[node]]
                if isnode(dest):
                    dest = translation[dest]
                xs.append((relation, dest))

    def decapitate(self, relation, reverse=False):
        oldhead = self.head
        self.head = self.add_node()
        if reverse:
            self.nodes[oldhead].append((relation, self.head))
        else:
            self.nodes[self.head].append((relation, oldhead))

    def add_data(self, relation, value):
        """
        You should not use this to relate nodes in the graph, only to add
        data fields to a node.
        To relate nodes in a graph use a combination of merge and decapitate.
        """
        assert not isnode(value)
        self.nodes[self.head].append((relation, value))

    def iter_nodes(self):
        return xrange(len(self.nodes))

    def iter_edges(self, node):
        return iter(self.nodes[node])

    def __add__(self, other):
        new = deepcopy(self)
        new.merge(other)
        return new

    def __iadd__(self, other):
        self.merge(other)
        return self

    def __len__(self):
        return len(self.nodes)


def make_canonical_expression(e):
    i = 0
    q = [e.get_head()]
    seen = set()
    while i != len(q):
        node = q[i]
        i += 1
        assert node not in seen, "Nouuu, expression is cyclic!"
        for relation, child in e.iter_edges(node):
            if isnode(child):
                q.append(child)
    q.reverse()
    canon = {}
    for node in q:
        childs = []
        for label, child in e.iter_edges(node):
            if isnode(child):
                child = canon[child]
            childs.append((label, child))
        childs.sort()
        canon[node] = tuple(childs)
    return canon[e.get_head()]


if __name__ == "__main__":
    from printout import expression_to_dot, expression_to_sparql

    def HasKeyword(x):
        e = Expression()
        e.add_data("Keyword", x)
        return e

    def HasTopic(e, reverse=False):
        e.decapitate("HasTopic", reverse)
        return e

    def WasBornIn(e, reverse=False):
        e.decapitate("WasBornIn", reverse)
        return e

    poet = HasKeyword("poet") + HasKeyword("famous")
    drama = HasKeyword("drama")
    germany = HasKeyword("germany")
    E = poet + HasTopic(drama) + WasBornIn(germany)
    print expression_to_dot(E)
    print expression_to_sparql(E)[1]
    from pprint import pprint
    pprint(make_canonical_expression(E))
