# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Implements the Quepy Application API
"""

import logging
from types import ModuleType

from quepy import settings
from quepy.regex import RegexTemplate
from quepy.tagger import get_tagger, TaggingError
from quepy.printout import expression_to_sparql
from quepy.encodingpolicy import encoding_flexible_conversion

logger = logging.getLogger("quepy.quepyapp")


class QuepyImportError(Exception):
    """ Error importing a quepy file. """


def install(app_name):
    """
    Installs the application and gives an QuepyApp object
    """

    module_paths = {
        u"settings": u"{0}.settings",
        u"regex": u"{0}.regex",
        u"semantics": u"{0}.semantics",
    }
    modules = {}

    for module_name, module_path in module_paths.iteritems():
        try:
            modules[module_name] = __import__(module_path.format(app_name),
                                              fromlist=[None])
        except ImportError, error:
            message = u"Error importing {0!r}: {1}"
            raise QuepyImportError(message.format(module_name, error))

    return QuepyApp(**modules)


class QuepyApp(object):
    """
    Provides the quepy application API.
    """

    def __init__(self, regex, settings, semantics):
        """
        Creates the application based on `regex`, `settings` and
        `semantics` modules.
        """

        assert isinstance(regex, ModuleType)
        assert isinstance(settings, ModuleType)
        assert isinstance(semantics, ModuleType)

        self._regex_module = regex
        self._settings_module = settings
        self._semantics_module = semantics

        # Save the settings right after loading settings module
        self._save_settings_values()

        self.tagger = get_tagger()

        self.rules = []
        for element in dir(self._regex_module):
            element = getattr(self._regex_module, element)

            try:
                if issubclass(element, RegexTemplate) and \
                        element is not RegexTemplate:

                    self.rules.append(element())
            except TypeError:
                continue

        self.rules.sort(key=lambda x: x.weight, reverse=True)

    def get_query(self, question):
        """
        Given `question` in natural language, it returns
        three things:

        - the target of the query in string format
        - the query
        - metadata given by the regex programmer (defaults to None)

        The query returned corresponds to the first regex that matches in
        weight order.
        """
        for target, sparql_query, userdata in self.get_queries(question):
            return target, sparql_query, userdata
        return None, None, None

    def get_queries(self, question):
        """
        Given `question` in natural language, it returns
        three things:

        - the target of the query in string format
        - the query
        - metadata given by the regex programmer (defaults to None)

        The queries returned corresponds to the regexes that match in
        weight order.
        """
        question = encoding_flexible_conversion(question)
        for expression, userdata in self._iter_compiled_forms(question):
            target, sparql_query = expression_to_sparql(expression)
            logger.debug(u"Semantics {1}: {0}".format(str(expression),
                         expression.rule_used))
            logger.debug(u"Query generated: {0}".format(sparql_query))
            yield target, sparql_query, userdata

    def _iter_compiled_forms(self, question):
        """
        Returns all the compiled form of the question.
        """

        try:
            words = list(self.tagger(question))
        except TaggingError:
            logger.warning(u"Can't parse tagger's output for: '%s'",
                           question)
            return

        logger.debug(u"Tagged question:\n" +
                     u"\n".join(u"\t{}".format(w.fullstr()) for w in words))

        for rule in self.rules:
            expression, userdata = rule.get_semantics(words)
            if expression:
                yield expression, userdata

    def _save_settings_values(self):
        """
        Persists the settings values of the app to the settings module
        so it can be accesible from another part of the software.
        """

        for key in dir(self._settings_module):
            if key.upper() == key:
                value = getattr(self._settings_module, key)
                if isinstance(value, str):
                    value = encoding_flexible_conversion(value)
                setattr(settings, key, value)
