#!/usr/bin/env python
# coding: utf-8

# Copyright (c) 2012, Machinalis S.R.L.
# This file is part of quepy and is distributed under the Modified BSD License.
# You should have received a copy of license in the LICENSE file.
#
# Authors: Rafael Carrascosa <rcarrascosa@machinalis.com>
#          Gonzalo Garcia Berrotaran <ggarcia@machinalis.com>

"""
System utility
"""

import os
import subprocess
import shutil
from contextlib import contextmanager
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper, mkdtemp


def pjoin(*x):
    return os.path.abspath(os.path.join(*x))

copy = shutil.copy
copyfile = shutil.copyfile
move = shutil.move


def rmr(x, directory=None, delete=True, ignore_errors=False):
    """
    Bye bye `x`
    """

    if delete:
        if directory is not None:
            x = pjoin(directory, x)
        if os.path.isdir(x):
            shutil.rmtree(x, ignore_errors=ignore_errors)
        else:
            try:
                os.remove(x)
            except OSError:
                if not ignore_errors:
                    raise


@contextmanager
def open_and_rm(name, directory, delete=True):
    name = pjoin(directory, name)
    try:
        yield open(name, "w")
    finally:
        rmr(name, delete=delete)


@contextmanager
def yield_and_rm(name, delete=True):
    try:
        yield name
    finally:
        if delete:
            rmr(name, delete=delete)


class ExecutionError(Exception):
    pass


class ExecutionContext:
    def __init__(self, name=None, directory=None, delete=True):
        if name is None:
            name = ""
        if directory is None:
            directory = "/tmp"
        self.name = name
        self.directory = directory
        self.delete = delete
        self.memory = []

    def tmpfile(self, prefix=None, suffix=".tmp", fullname=None,
                delete=None):
        if delete is None:
            delete = self.delete
        if fullname is not None:
            path = self.pathname(fullname)
            f = open(path, "w+")
            if delete:
                f = _TemporaryFileWrapper(f, f.name)
        else:
            if prefix is None:
                prefix = self.name + "_"
            else:
                prefix = "{0}_{1}_".format(self.name, prefix)
            f = NamedTemporaryFile(prefix=prefix, suffix=suffix,
                                   dir=self.directory, delete=delete)
        self.memory.append(f)
        return f

    def runcmd(self, cmdline, stdin=None, stdout=None,
               stderr=None, env=None):
        pname = cmdline.split()[0]
        if stdin is None:
            stdin = open("/dev/null")
        if stdout is None:
            stdout = self.tmpfile("output")
        if stderr is None:
            stderr = self.tmpfile("error")
        # print "Running {0} < {1} > {2} 2> {3}".format(cmdline,
        #                                                     stdin.name,
        #                                                     stdout.name,
        #                                                    stderr.name)
        try:
            status = subprocess.call(cmdline.split(),
                                     stdin=stdin,
                                     stdout=stdout,
                                     stderr=stderr,
                                     env=env)
        except OSError as e:
            s = "While running {1}: {0.strerror}, is {1} in PATH?"
            raise ExecutionError(s.format(e, pname))
        if status != 0:
            errlog = stderr
            if self.delete:
                errlog = self.tmpfile(prefix="error", delete=False)
                stderr.seek(0)
                shutil.copyfile(stderr.name, errlog.name)
            s = "{2} returned with status {0}, " + \
                "check the error output in {1}"
            raise ExecutionError(s.format(status, errlog.name, pname))
        return stdout, stderr

    def rmr(self, x, delete=None, ignore_errors=False):
        if delete is None:
            delete = self.delete
        rmr(self.pathname(x), delete=delete, ignore_errors=ignore_errors)

    def exists(self, x):
        return os.path.exists(self.pathname(x))

    def pathname(self, *x):
        return pjoin(*((self.directory,) + x))

    def tmpdir(self, prefix=None, fullname=None,
               delete=None):
        if delete is None:
            delete = self.delete
        if fullname is not None:
            path = self.pathname(fullname)
            if os.path.exists(path):
                rmr(path)
            os.mkdir(path)
        else:
            if prefix is None:
                prefix = self.name + "_"
            else:
                prefix = "{0}_{1}_".format(self.name, prefix)
            path = mkdtemp(prefix=prefix, dir=self.directory)
        return yield_and_rm(path, self.delete)

    def retrieve(self, x):
        basename = os.path.basename(x)
        if self.exists(basename):
            path = self.pathname(basename)
            if path == x:
                return
            os.remove(path)
        if self.delete:
            shutil.move(x, self.directory)
        else:
            shutil.copy(x, self.directory)
