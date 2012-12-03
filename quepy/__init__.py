#!/usr/bin/env python
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

VERSION = 0.1

from quepy.quepyapp import install, QuepyApp, QuepyImportError
from quepy.printout import set_loglevel
