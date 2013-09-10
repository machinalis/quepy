# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
Quepy converts Natural Language Question to database queries.
"""

VERSION = 0.2

import logging
from quepy.quepyapp import install, QuepyApp


def set_loglevel(level=logging.WARNING):
    logger = logging.getLogger("quepy")
    logger.setLevel(level)
