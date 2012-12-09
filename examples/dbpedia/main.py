#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Main script for DBpedia quepy.
"""

import sys
import time
import random
import datetime

import quepy
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
dbpedia = quepy.install("dbpedia")

# quepy.set_loglevel("DEBUG")


def print_define(results, target, metadata=None):
    for result in results["results"]["bindings"]:
        if result[target]["xml:lang"] == "en":
            print result[target]["value"]
            print


def print_enum(results, target, metadata=None):
    used_labels = []

    for result in results["results"]["bindings"]:
        if result[target]["type"] == u"literal":
            if result[target]["xml:lang"] == "en":
                label = result[target]["value"]
                if label not in used_labels:
                    used_labels.append(label)
                    print label


def print_literal(results, target, metadata=None):
    for result in results["results"]["bindings"]:
        literal = result[target]["value"]
        if metadata:
            print metadata.format(literal)
        else:
            print literal


def print_time(results, target, metadata=None):
    gmt = time.mktime(time.gmtime())
    gmt = datetime.datetime.fromtimestamp(gmt)

    for result in results["results"]["bindings"]:
        offset = result[target]["value"].replace(u"−", u"-")

        if "to" in offset:
            from_offset, to_offset = offset.split("to")
            from_offset, to_offset = int(from_offset), int(to_offset)

            if from_offset > to_offset:
                from_offset, to_offset = to_offset, from_offset

            from_delta = datetime.timedelta(hours=from_offset)
            to_delta = datetime.timedelta(hours=to_offset)

            from_time = gmt + from_delta
            to_time = gmt + to_delta

            location_string = random.choice(["where you are",
                                             "your location"])

            print "Between %s and %s, depending %s" % \
                  (from_time.strftime("%H:%M"),
                   to_time.strftime("%H:%M on %A"),
                   location_string)

        else:
            offset = int(offset)

            delta = datetime.timedelta(hours=offset)
            the_time = gmt + delta

            print the_time.strftime("%H:%M on %A")


def print_age(results, target, metadata=None):
    assert len(results["results"]["bindings"]) == 1

    birth_date = results["results"]["bindings"][0][target]["value"]
    year, month, days = birth_date.split("-")

    birth_date = datetime.date(int(year), int(month), int(days))

    now = datetime.datetime.utcnow()
    now = now.date()

    age = now - birth_date
    print "{} years old".format(age.days / 365)


def wikipedia2dbpedia(wikipedia_url):
    """
    Given a wikipedia URL returns the dbpedia resource
    of that page.
    """

    query = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT * WHERE {
        ?url foaf:isPrimaryTopicOf <%s>.
    }
    """ % wikipedia_url

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    if not results["results"]["bindings"]:
        print "Snorql URL not found"
        sys.exit(1)
    else:
        return results["results"]["bindings"][0]["url"]["value"]


if __name__ == "__main__":
    default_questions = [
        "What is a car?",
        "Who is Tom Cruise?",
        "Who is George Lucas?",
        "Who is Mirtha Legrand?",
        # "List Microsoft software",
        "Name Fiat cars",
        "time in argentina",
        "what time is it in Chile?",
        "List movies directed by Martin Scorsese",
        "How long is Pulp Fiction",
        "which movies did Mel Gibson starred?",
        "When was Gladiator released?",
        "who directed Pocahontas?",
        "actors of Fight Club",
    ]

    if "-d" in sys.argv:
        quepy.set_loglevel("DEBUG")
        sys.argv.remove("-d")

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])

        if question.count("wikipedia.org"):
            print wikipedia2dbpedia(sys.argv[1])
            sys.exit(0)
        else:
            questions = [question]
    else:
        questions = default_questions

    print_handlers = {
        "define": print_define,
        "enum": print_enum,
        "time": print_time,
        "literal": print_literal,
        "age": print_age,
    }

    for question in questions:
        print question
        print "-" * len(question)

        target, query, metadata = dbpedia.get_query(question)

        if isinstance(metadata, tuple):
            query_type = metadata[0]
            metadata = metadata[1]
        else:
            query_type = metadata
            metadata = None

        if query is None:
            print "Query not generated :(\n"
            continue

        print query

        if target.startswith("?"):
            target = target[1:]
        if query:
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            if not results["results"]["bindings"]:
                print "No answer found :("
                continue

        print_handlers[query_type](results, target, metadata)
        print
