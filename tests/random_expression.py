# -*- coding: utf-8 -*-
import random
from quepy.expression import Expression


def random_data(only_ascii=False):
    data = []
    first = True
    while first or 1 / 20.0 < random.random():
        first = False
        if only_ascii:
            c = unichr(random.randint(33, 126))
            data.append(c)
            continue
        x = random.random()
        if 0.1 > x:
            c = random.choice(u" ./\n")
        elif 0.50 > x:
            c = unichr(random.randint(65, 122))
        elif 0.85 > x:
            c = unichr(random.randint(0, 127))
        else:
            c = unichr(random.randint(0, 65535))
        data.append(c)
    return u"".join(data)


def random_relation(only_ascii=False):
    data = random_data(only_ascii)
    data = data.replace(" ", "")
    if random.random() > 0.05:
        return data

    class UnicodeableDummy(object):
        def __unicode__(self):
            return data
    return UnicodeableDummy()


def random_expression(only_ascii=False):
    """
    operations: new node, add data, decapitate, merge
    """
    mean_size = 20
    xs = [40.0, 30.0, 50.0, 20.0]
    xs = [x * (1.0 - random.random()) for x in xs]
    assert all(x != 0 for x in xs)
    new_node, add_data, decapitate, _ = [x / sum(xs) for x in xs]
    expressions = [Expression(), Expression(), Expression(), Expression()]
    while len(expressions) != 1:
        if (1.0 / mean_size) < random.random():
            # Will start to merge more and will not create new nodes
            new_node = 0.0
        # Choose action
        r = random.random()
        if r < new_node:
            # New expression
            expressions.append(Expression())
        elif r < add_data + new_node:
            # Add data
            e = random.choice(expressions)
            e.add_data(random_relation(only_ascii), random_data(only_ascii))
        elif r < decapitate + add_data + new_node:
            # Decapitate
            e = random.choice(expressions)
            e.decapitate(random_relation(only_ascii),
                         reverse=(0.25 < random.random()))
        elif len(expressions) != 1:
            # Merge
            random.shuffle(expressions)
            e2 = expressions.pop()
            e1 = expressions[-1]
            e1 += e2
    return expressions[0]
