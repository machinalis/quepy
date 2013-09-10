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
from importlib import import_module
from types import ModuleType

from quepy import settings
from quepy import generation
from quepy.parsing import QuestionTemplate
from quepy.tagger import get_tagger, TaggingError
from quepy.encodingpolicy import encoding_flexible_conversion

logger = logging.getLogger("quepy.quepyapp")


def install(app_name):
    """
    Installs the application and gives an QuepyApp object
    """

    module_paths = {
        u"settings": u"{0}.settings",
        u"parsing": u"{0}",
    }
    modules = {}

    for module_name, module_path in module_paths.iteritems():
        try:
            modules[module_name] = import_module(module_path.format(app_name))
        except ImportError, error:
            message = u"Error importing {0!r}: {1}"
            raise ImportError(message.format(module_name, error))

    return QuepyApp(**modules)


def question_sanitize(question):
    question = question.replace("'", "\'")
    question = question.replace("\"", "\\\"")
    return question


class QuepyApp(object):
    """
    Provides the quepy application API.
    """

    def __init__(self, parsing, settings):
        """
        Creates the application based on `parsing`, `settings` modules.
        """

        assert isinstance(parsing, ModuleType)
        assert isinstance(settings, ModuleType)

        self._parsing_module = parsing
        self._settings_module = settings

        # Save the settings right after loading settings module
        self._save_settings_values()

        self.tagger = get_tagger()
        self.language = getattr(self._settings_module, "LANGUAGE", None)
        if not self.language:
            raise ValueError("Missing configuration for language")

        self.rules = []
        for element in dir(self._parsing_module):
            element = getattr(self._parsing_module, element)

            try:
                if issubclass(element, QuestionTemplate) and \
                        element is not QuestionTemplate:

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

        question = question_sanitize(question)
        for target, query, userdata in self.get_queries(question):
            return target, query, userdata
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
            target, query = generation.get_code(expression, self.language)
            message = u"Interpretation {1}: {0}"
            logger.debug(message.format(str(expression),
                         expression.rule_used))
            logger.debug(u"Query generated: {0}".format(query))
            yield target, query, userdata

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
                     u"\n".join(u"\t{}".format(w for w in words)))

        for rule in self.rules:
            expression, userdata = rule.get_interpretation(words)
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
