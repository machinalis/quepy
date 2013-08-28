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

api_key = ""
service_url = 'https://www.googleapis.com/freebase/v1/mqlread'
freebase = quepy.install("freebase")


if __name__ == "__main__":
    args = docopt(__doc__)
    question = " ".join(args["<question>"])
    target, query, metadata = freebase.get_query(question)
    print query

    if args["--request"]:
        print
        params = {'query': query, 'key': api_key}
        url = service_url + '?' + urllib.urlencode(params)
        responses = json.loads(urllib.urlopen(url).read())
        if "error" in responses:
            print responses
            exit()

        if responses:
            for response in responses["result"]:
                result = response
                for key in target:
                    result = response[key]

                if result is not None:
                    print result["value"]
                else:
                    print "<No value avaliable>"
