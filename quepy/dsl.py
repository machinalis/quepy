# coding: utf-8
# pylint: disable=C0111

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Domain specific language definitions.
"""

from copy import copy
from quepy.expression import Expression
from quepy.encodingpolicy import encoding_flexible_conversion


class FixedRelation(Expression):
    """
    Expression for a fixed relation. It states that "A is related to B"
    through the relation defined in `relation`.
    """

    relation = None
    reverse = False

    def __init__(self, destination, reverse=None):
        if reverse is None:
            reverse = self.reverse
        super(FixedRelation, self).__init__()
        if self.relation is None:
            raise ValueError("You *must* define the `relation` "
                             "class attribute to use this class.")
        self.nodes = copy(destination.nodes)
        self.head = destination.head
        self.decapitate(self.relation, reverse)


class FixedType(Expression):
    """
    Expression for a fixed type.
    This captures the idea of something having an specific type.
    """

    fixedtype = None
    fixedtyperelation = u"rdf:type"  # FIXME: sparql specific

    def __init__(self):
        super(FixedType, self).__init__()
        if self.fixedtype is None:
            raise ValueError("You *must* define the `fixedtype` "
                             "class attribute to use this class.")
        self.fixedtype = encoding_flexible_conversion(self.fixedtype)
        self.fixedtyperelation = \
            encoding_flexible_conversion(self.fixedtyperelation)
        self.add_data(self.fixedtyperelation, self.fixedtype)


class FixedDataRelation(Expression):
    """
    Expression for a fixed relation. This is
    "A is related to Data" through the relation defined in `relation`.
    """

    relation = None
    language = None

    def __init__(self, data):
        super(FixedDataRelation, self).__init__()
        if self.relation is None:
            raise ValueError("You *must* define the `relation` "
                             "class attribute to use this class.")
        self.relation = encoding_flexible_conversion(self.relation)
        if self.language is not None:
            self.language = encoding_flexible_conversion(self.language)
            data = u"\"{0}\"@{1}".format(data, self.language)
        self.add_data(self.relation, data)


class HasKeyword(FixedDataRelation):
    """
    Abstraction of an information retrival key, something standarized used
    to look up things in the database.
    """
    relation = u"quepy:Keyword"

    def __init__(self, data):
        data = self.sanitize(data)
        super(HasKeyword, self).__init__(data)

    @staticmethod
    def sanitize(text):
        # User can redefine this method if needed
        return text


class HasType(FixedRelation):
    relation = "rdf:type"


class IsRelatedTo(FixedRelation):
    pass
# Looks weird, yes, here I am using `IsRelatedTo` as a unique identifier.
IsRelatedTo.relation = IsRelatedTo
