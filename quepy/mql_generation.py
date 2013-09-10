# -*- coding: utf-8 -*-

import re
import json
from quepy.dsl import IsRelatedTo
from quepy.expression import isnode
from quepy.encodingpolicy import encoding_flexible_conversion


def choose_start_node(e):
    """
    Choose a node of the `Expression` such that no property leading to a data
    has to be reversed (with !).
    """
    # Since data "nodes" have no outgoing edges it sufices to find any node
    # with an outgoing edge.
    for node in e.iter_nodes():
        if list(e.iter_edges(node)):
            return node
    return node


def safely_to_unicode(x):
    """
    Given an "edge" (a relation) or "a data" from an `Expression` graph
    transform it into a unicode string fitted for insertion into a MQL query.
    """
    if isinstance(x, unicode):
        return x
    if isinstance(x, str):
        return encoding_flexible_conversion(x)
    if isinstance(x, IsRelatedTo):
        return u"/type/reflect/any_master"
    return unicode(x)  # FIXME: Any object is unicode-able, this is error prone


def to_bidirected_graph(e):
    """
    Rewrite the graph such that there are reversed edges for every forward
    edge.
    If an edge goes into a data, it should not be reversed.
    """
    graph = {node: [] for node in e.iter_nodes()}
    for node in e.iter_nodes():
        for relation, other in e.iter_edges(node):
            relation = safely_to_unicode(relation)
            if isnode(other):
                graph[other].append((u"!" + relation, node))
            else:
                other = safely_to_unicode(other)
            graph[node].append((relation, other))
    assert all(isnode(x) for x in graph) and len(e) == len(graph)
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
    """
    Generates paths from `start` to every other node in `graph` and puts it in
    the returned dictionary `paths`.
    ie.: `paths_from_node(graph, start)[node]` is a list of the edge names used
    to get to `node` form `start`.
    """
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
    """
    Generates a MQL query for the `Expression` `e`.
    """
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
                    continue  # other is not in post_order_depth_first order
            d[relation] = other
        generated[node] = [d]

    mql_query = json.dumps(generated[start], sort_keys=True,
                            indent=2, separators=(',', ': '))
    mql_query = _tidy(mql_query)
    target = paths_from_root(graph, start)[e.get_head()]
    return target, mql_query


def _tidy(mql):
    """
    Given a json representing a MQL query it collapses spaces between
    braces and curly braces to make it look tidy.
    """
    def replacement_function(match):
        text = match.group(0)
        if text.startswith("[") and text.endswith("]"):
            return "[{}]"
        elif text.startswith("["):
            return "[{"
        indent = 0
        match = re.search("}[ \t]*\n(\s*?)\]", text)
        if match:
            indent = len(match.group(1))
        return " " * indent + "}]"
    return re.sub("\[\s*{\s*}\s*\]|\[\s+{|[ \t]*}\s+\]",
                  replacement_function, mql)
