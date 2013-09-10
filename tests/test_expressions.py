#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Tests for expressions.
"""

import unittest
from quepy.expression import Expression, isnode


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


class ExpressionTests(object):
    def test_acyclic(self):
        head = self.e.get_head()
        q = [head]
        seen = set()
        while q:
            current = q.pop()
            self.assertNotIn(current, seen)
            seen.add(current)
            for relation, child in self.e.iter_edges(current):
                if isnode(child):
                    q.append(child)

    def test_non_empty(self):
        self.assertNotEqual(len(self.e), 0)

    def test_add_data(self):
        rel = u"|@·~½"
        data = "somedata"
        self.e.add_data(rel, data)
        xs = list(self.e.iter_edges(self.e.get_head()))
        self.assertIn((rel, data), xs)

    def test_decapitate(self):
        oldhead = self.e.get_head()
        self.e.decapitate("blabla")
        self.assertNotEqual(oldhead, self.e.get_head())
        xs = list(self.e.iter_edges(self.e.get_head()))
        self.assertEqual(xs, [("blabla", oldhead)])

    def test_merges1(self):
        oldlen = len(self.e)
        oldhead = self.e.get_head()
        other = Expression()
        other.decapitate("blabla")
        self.e.merge(other)
        self.assertEqual(self.e.get_head(), oldhead)
        self.assertEqual(len(self.e), oldlen + len(other) - 1)

    def test_merges2(self):
        other = Expression()
        other.decapitate("blabla")
        oldlen = len(other)
        oldhead = other.get_head()
        other.merge(self.e)
        self.assertEqual(other.get_head(), oldhead)
        self.assertEqual(len(other), oldlen + len(self.e) - 1)

    def test_plus_makes_copy(self):
        other = Expression()
        other.decapitate("blabla")
        a = self.e + other
        self.assertFalse(a is other or self.e is other or a is self.e)

    def test_plus_is_conmutative(self):
        other = Expression()
        other.decapitate("blabla")
        a = self.e + other
        b = other + self.e
        self.assertEqual(make_canonical_expression(a),
                         make_canonical_expression(b))

    def test_plus_is_conmutative2(self):
        other = Expression()
        other.decapitate("blabla")
        a = self.e + other + self.e
        b = other + self.e + self.e
        self.assertEqual(make_canonical_expression(a),
                         make_canonical_expression(b))


class TestExpression1(unittest.TestCase, ExpressionTests):
    def setUp(self):
        self.e = Expression()


class TestExpression2(unittest.TestCase, ExpressionTests):
    def setUp(self):
        self.e = Expression()
        self.e.add_data("key", "1")
        self.e.add_data("key", "2")
        self.e.add_data(u"~·~··@↓", None)
        self.e.add_data(None, None)


class TestExpression3(unittest.TestCase, ExpressionTests):
    def setUp(self):
        self.e = Expression()
        self.e.add_data("key", "1")
        self.e.decapitate(u"µ")
        self.e.add_data("a", "2")
        self.e.add_data("a", "3")
        self.e.add_data(None, None)
        self.e.decapitate(None)
        self.e.add_data(None, None)


class TestExpression4(unittest.TestCase, ExpressionTests):
    def setUp(self):
        self.e = Expression()
        self.e.add_data(123, "456")
        other = Expression()
        other.add_data(0, "1")
        other.add_data(2, "3")
        other.decapitate("iuju")
        for _ in xrange(5):
            self.e.decapitate("nouu")
            self.e += other


class CanonEqualTest(object):
    def test_are_the_same(self):
        a = make_canonical_expression(self.a)
        b = make_canonical_expression(self.b)
        self.assertEqual(a, b)


class CanonNotEqualTest(object):
    def test_are_the_same(self):
        a = make_canonical_expression(self.a)
        b = make_canonical_expression(self.b)
        self.assertNotEqual(a, b)


class TestCanon1(unittest.TestCase, CanonEqualTest):
    def setUp(self):
        self.a = Expression()
        self.b = Expression()


class TestCanon2(unittest.TestCase, CanonEqualTest):
    def setUp(self):
        self.a = Expression()
        self.a.add_data(None, "1")
        self.a.add_data(None, "2")
        self.b = Expression()
        self.b.add_data(None, "2")
        self.b.add_data(None, "1")


class TestCanon3(unittest.TestCase, CanonEqualTest):
    def setUp(self):
        A = Expression()
        A.add_data("bla", "somedata")
        A.decapitate("hier")
        B = Expression()
        B.add_data("ble", "otherdata")
        B.decapitate("hier")
        self.a = A + B
        self.b = B + A


class TestCanon4(unittest.TestCase, CanonEqualTest):
    def setUp(self):
        A = Expression()
        A.add_data("bla", "somedata")
        A.decapitate("hier")
        B = Expression()
        B.add_data("ble", "otherdata")
        B.decapitate("hier")
        C = A + B
        C.decapitate("hier")
        C += B
        C.decapitate("hier")
        self.a = C + A
        D = B + A
        D.decapitate("hier")
        D += B
        D.decapitate("hier")
        self.b = D + A


class TestCanon95(unittest.TestCase, CanonNotEqualTest):
    def setUp(self):
        self.a = Expression()
        self.a.decapitate("onelevel")

        self.b = Expression()
        self.b.decapitate("onelevel", reverse=True)


class TestCanon96(unittest.TestCase, CanonNotEqualTest):
    def setUp(self):
        self.a = Expression()
        self.a.add_data(0, "data")
        self.a.decapitate("onelevel")

        self.b = Expression()
        self.b.add_data(0, "data")
        self.b.decapitate("onelevel", reverse=True)


class TestCanon97(unittest.TestCase, CanonNotEqualTest):
    def setUp(self):
        other = Expression()
        other.decapitate("onelevel")
        self.a = Expression()
        for _ in xrange(5):
            self.a.decapitate("step")
            self.a += other

        other = Expression()
        other.decapitate("onelevel", reverse=True)
        self.b = Expression()
        for _ in xrange(5):
            self.b.decapitate("step")
            self.b += other


class TestCanon98(unittest.TestCase, CanonNotEqualTest):
    def setUp(self):
        other = Expression()
        other.add_data(0, "data")
        other.decapitate("onelevel")
        self.a = Expression()
        for _ in xrange(5):
            self.a.decapitate("step")
            self.a += other

        other = Expression()
        other.add_data(0, "data")
        other.decapitate("onelevel", reverse=True)
        self.b = Expression()
        for _ in xrange(5):
            self.b.decapitate("step")
            self.b += other


class TestCanon99(unittest.TestCase, CanonNotEqualTest):
    def setUp(self):
        self.a = Expression()
        self.b = Expression()
        self.b.decapitate("relation")


if __name__ == "__main__":
    unittest.main()
