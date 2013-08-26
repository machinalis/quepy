# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
This file implements the ``Expression`` class.

``Expression`` is the base class for all the semantic representations in quepy.
It's meant to carry all the information necessary to build a database query in
an abstract form.

By desing it's aimed specifically to represent a SPARQL query, but it should
be able to represent queries in other database languages too.

A (simple) SPARQL query can be thought as a subgraph that has to match into a
larger graph (the database). Each node of the subgraph is a variable and every
edge a relation. So in order to represent a query, ``Expression`` implements a
this subgraph using adjacency lists.

Also, ``Expression`` instances are meant to be combined with each other somehow
to make complex queries out of simple ones (this is one main objectives
of quepy).

To do that, every ``Expression`` has a special node called the ``head``, which
is the target node (variable) of the represented query. All operations over
``Expression`` instances work on the ``head`` node, leaving the rest of the
nodes intact.

So ``Expression`` graphs are not built by explicitly adding nodes and edges
like any other normal graph. Instead they are built by a combination of the
following basic operations:

    - ``__init__``: When a ``Expression`` is instantiated a single solitary
                    node is created in the graph.

    - ``decapitate``: Creates a blank node and makes it the new ``head`` of the
                    ``Expression``. Then it adds an edge (a relation) linking
                    this new head to the old one. So in a single operation a
                    node and an edge are added. Used to represent stuff like
                    ``?x rdf:type ?y``.

    - ``add_data``: Adds a relation into some constant data from the ``head``
                    node of the ``Expression``. Used to represent stuff like
                  ``?x rdf:label "John Von Neumann"``.

    - ``merge``: Given two ``Expressions``, it joins their graphs preserving
                 every node and every edge intact except for their ``head``
                 nodes.
                 The ``head`` nodes are merged into a single node that is the
                 new ``head`` and shares all the edges of the previous heads.
                 This is used to combine two graphs like this:

               ::

                   A = ?x rdf:type ?y
                   B = ?x rdf:label "John Von Neumann"

               Into a new one:

               ::

                   A + B = ?x rdf:type ?y;
                           ?x rdf:label "John Von Neumann"


You might be saying "Why?! oh gosh why you did it like this?!".
The reasons are:

    - It allows other parts of the code to build queries in a super
      intuive language, like ``IsPerson() + HasKeyword("Russell")``.
      Go and see the DBpedia example.

    - You can only build connected graphs (ie, no useless variables in query).

    - You cannot have variable name clashes.

    - You cannot build cycles into the graph (could be a con to some, a
      plus to other(it's a plus to me))

    - There are just 3 really basic operations and their semantics are defined
      consisely without special cases (if you care for that kind of stuff
      (I do)).
"""


from collections import defaultdict
from copy import deepcopy


def isnode(x):
    return isinstance(x, int)


class Expression(object):

    def __init__(self):
        """
        Creates a new graph with a single solitary blank node.
        """
        self.nodes = []
        self.head = self._add_node()

    def _add_node(self):
        """
        Adds a blank node to the graph and returns it's index (a unique
        identifier).
        """
        i = len(self.nodes)
        self.nodes.append([])
        return i

    def get_head(self):
        """
        Returns the index (the unique identifier) of the head node.
        """
        return self.head

    def merge(self, other):
        """
        Given other Expression, it joins their graphs preserving every
        node and every edge intact except for the ``head`` nodes.
        The ``head`` nodes are merged into a single node that is the new
        ``head`` and shares all the edges of the previous heads.
        """
        translation = defaultdict(self._add_node)
        translation[other.head] = self.head
        for node in other.iter_nodes():
            for relation, dest in other.iter_edges(node):
                xs = self.nodes[translation[node]]
                if isnode(dest):
                    dest = translation[dest]
                xs.append((relation, dest))

    def decapitate(self, relation, reverse=False):
        """
        Creates a new blank node and makes it the ``head`` of the
        Expression. Then it adds an edge (a ``relation``) linking the
        the new head to the old one. So in a single operation a
        node and an edge are added.
        If ``reverse`` is ``True`` then the ``relation`` links the old head to
        the new head instead of the opposite (some relations are not
        commutative).
        """
        oldhead = self.head
        self.head = self._add_node()
        if reverse:
            self.nodes[oldhead].append((relation, self.head))
        else:
            self.nodes[self.head].append((relation, oldhead))

    def add_data(self, relation, value):
        """
        Adds a ``relation`` to some constant ``value`` to the ``head`` of the
        Expression.
        ``value`` is recommended be of type:
        - ``unicode``
        - ``str`` and can be decoded using the default encoding (settings.py)
        - A custom class that implements a ``__unicode__`` method.
        - It can *NEVER* be an ``int``.

        You should not use this to relate nodes in the graph, only to add
        data fields to a node.
        To relate nodes in a graph use a combination of merge and decapitate.
        """
        assert not isnode(value)
        self.nodes[self.head].append((relation, value))

    def iter_nodes(self):
        """
        Iterates the indexes (the unique identifiers) of the Expression nodes.
        """
        return xrange(len(self.nodes))

    def iter_edges(self, node):
        """
        Iterates over the pairs: ``(relation, index)`` which are the neighbors
        of ``node`` in the expression graph, where:
        - ``node`` is the index of the node (the unique identifier).
        - ``relation`` is the label of the edge between the nodes
        - ``index`` is the index of the neighbor (the unique identifier).
        """
        return iter(self.nodes[node])

    def __add__(self, other):
        """
        Merges ``self`` and ``other`` in a new Expression instance.
        Ie, ``self`` and ``other`` are not modified.
        """
        new = deepcopy(self)
        new.merge(other)
        return new

    def __iadd__(self, other):
        """
        Merges ``self`` and ``other`` into ``self``
        ``other`` is not modified but the original data in ``self`` is lost.
        """
        self.merge(other)
        return self

    def __len__(self):
        """
        Amount of nodes in the graph.
        """
        return len(self.nodes)
