# -*- coding: utf-8 -*-
from collections import defaultdict
from quepy.expression import isnode
from quepy.intermediate_representation import IsRelatedTo
import json


class MQLJSON(json.JSONEncoder):
    def default(self, o):
        return unicode(o)


def choose_start_node(e):
    for node in e.iter_nodes():
        if list(e.iter_edges(node)):
            return node
    raise node


def to_bidirected_graph(e):
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
    s = json.dumps([generated[start]], sort_keys=True,
                    indent=4, separators=(',', ': '), cls=MQLJSON)
    return s, None


if __name__ == "__main__":
    from semantics import *

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
    person = HasName({}) + HoldsGovernmentPosition(president)
    print generate_mql(person)[0]
