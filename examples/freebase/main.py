#!/usr/bin/env python
# coding: utf-8

"""
Main script for freebase quepy.

Usage:
    main.py [options] <question> ...

Options:
    -r --request     Queries the online database and prints the results
"""

import json
import quepy
import urllib
from docopt import docopt

service_url = 'https://www.googleapis.com/freebase/v1/mqlread'
freebase = quepy.install("freebase")


def request(query):
    params = {'query': query}
    url = service_url + '?' + urllib.urlencode(params)
    responses = json.loads(urllib.urlopen(url).read())
    return responses


def result_from_responses(responses, target):
    if responses:
        to_explore = responses["result"]
        for key in target:
            _to_explore = []
            for elem in to_explore:
                for response in elem[key]:
                    _to_explore.append(response)
            to_explore = _to_explore

        result = []
        for elem in to_explore:
            if isinstance(elem, dict):
                if "lang" in elem:
                    if elem["lang"] == "/lang/en":
                        result.append(elem.get("value", elem))
                else:
                    result.append(elem.get("value", elem))
            else:
                result.append(elem)
        return result


if __name__ == "__main__":
    args = docopt(__doc__)
    question = " ".join(args["<question>"])
    target, query, metadata = freebase.get_query(question)
    print query

    if args["--request"]:
        print
        responses = request(query)
        if "error" in responses:
            print responses
            exit()
        else:
            for response in result_from_responses(responses, target):
                print response
