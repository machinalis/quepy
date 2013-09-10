# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Functions to do encoding checkings.
"""

import logging
from quepy import settings
logger = logging.getLogger("quepy.encodingpolicy")


def encoding_flexible_conversion(string, complain=False):
    """
    Converts string to the proper encoding if it's possible
    and if it's not raises a ValueError exception.

    If complain it's True, it will emit a logging warning about
    converting a string that had to be on the right encoding.
    """

    if isinstance(string, unicode):
        return string
    try:
        ustring = string.decode(settings.DEFAULT_ENCODING)
    except UnicodeError:
        message = u"Argument must be unicode or {}"
        raise ValueError(message.format(settings.DEFAULT_ENCODING))
    if complain:
        logger.warning(u"Forced to guess the encoding of {!r}, please "
                       u"provide a unicode string instead".format(string))
    return ustring


def assert_valid_encoding(string):
    """
    If string it's not in a valid encoding it raises a
    ValueError exception.
    """

    if not isinstance(string, unicode):
        raise ValueError(u"Argument must be unicode")
