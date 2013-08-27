# -*- coding: utf-8 -*-

from collections import defaultdict
from quepy.expression import isnode
from quepy.intermediate_representation import IsRelatedTo
import json


def choose_start_node(e):
    """
    Choose a node of the graph such that no property leading to a data has
    to be reversed (with !).
    """
    for node in e.iter_nodes():
        if list(e.iter_edges(node)):
            return node
    raise node


def to_bidirected_graph(e):
    """
    Rewrite the graph such that there are reversed edges for every forward
    edge.
    If an edge goes into a data, it should not be reversed.
    """
    graph = defaultdict(list)
    for node in e.iter_nodes():
        for relation, other in e.iter_edges(node):
            # Add IsRelatedTo handling here
            if relation is IsRelatedTo:
                relation = "/type/reflect/any_master"
            graph[node].append((relation, other))
            if isnode(other):
                graph[other].append(("!" + relation, node))
    return graph


def post_order_depth_first(graph, start):
    """
    Iterate over the nodes of the graph (is a tree) in a way such that every
    node is preceded by it's childs.
    `graph` is a dict that represents the `Expression` graph. It's a tree too
    beacuse Expressions are trees.
    `start` is the node to use as the root of the tree.
    """
    q = [start]
    seen = set()
    i = 0
    while i != len(graph):
        node = q[i]
        seen.add(node)
        i += 1
        for _, other in graph[node]:
            if isnode(other) and other not in seen:
                q.append(other)
    assert len(q) == len(graph)
    q.reverse()
    return q


def paths_from_root(graph, start):
    paths = {start: []}
    q = [start]
    seen = set()
    while q:
        node = q.pop()
        seen.add(node)
        for relation, child in graph[node]:
            if isnode(child) and child not in seen:
                q.append(child)
                paths[child] = paths[node] + [relation]
    return paths


def generate_mql(e):
    start = choose_start_node(e)
    graph = to_bidirected_graph(e)
    generated = {}
    for node in post_order_depth_first(graph, start):
        d = {}
        for relation, other in graph[node]:
            if isnode(other):
                try:
                    other = generated[other]
                except KeyError:
                    # Then other is backwards in the tree, and in wrong order
                    continue
            d[relation] = other
        generated[node] = d

    mql_query = json.dumps([generated[start]], sort_keys=True,
                            indent=4, separators=(',', ': '))
    target = paths_from_root(graph, start)[e.get_head()]
    return target, mql_query


if __name__ == "__main__":
    from intermediate_representation import *

    class NameOf(FixedRelation):
        relation = "/type/object/name"
        reverse = True

    class HasName(FixedDataRelation):
        relation = "/type/object/name"

    class GovernmentPosition(FixedDataRelation):
        relation = "/government/government_position_held/basic_title"

    class GovernmentPositionJusridiction(FixedRelation):
        relation = "/government/government_position_held/jurisdiction_of_office"

    class IsCountry(FixedType):
        fixedtype = "/location/country"
        fixedtyperelation = "/type/object/type"

    class HoldsGovernmentPosition(FixedRelation):
        relation = "/government/government_position_held/office_holder"
        reverse = True

    france = IsCountry() + HasName("France")
    president = GovernmentPosition("President") + \
                GovernmentPositionJusridiction(france)
    person = NameOf(HoldsGovernmentPosition(president))
    target, mql_query = generate_mql(person)
    print mql_query
    print "Target:", target
