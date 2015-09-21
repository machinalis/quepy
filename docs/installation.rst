Installation
============

Dependencies
------------

* `refo <http://github.com/machinalis/refo>`_
* `nltk <http://nltk.org/>`_ - *if you intend to use nltk tagger*
* `SPARQLWrapper <http://pypi.python.org/pypi/SPARQLWrapper>`_ *if you intend to use the examples*
* `graphviz <http://www.graphviz.org/>`_ *if you intend to visualize your queries*
* `doctopt <https://github.com/docopt/docopt>`_ *For beautiful command-line interfaces*



From pip
--------

If you have **pip** installed you can run:

::

    $ pip install quepy

then :ref:`check-installation`

From source code
----------------

Download the *GIT* repository from `Github <https://github.com/machinalis/quepy>`_ running:

::

    $ git clone https://github.com/machinalis/quepy.git

run the install script doing:

::

    $ cd quepy
    $ sudo python setup.py install

and then :ref:`check-installation`


.. _check-installation:

Checking the installation
-------------------------

To check if quepy was successfully installed run:

::

    $ quepy --version

and you should obtain the version number.


Set up the POS tagger
---------------------

After that you need to download the backend's POS tagger. It's ok if you don't
know what that is, it's safe to treat it like a black box.
Quepy uses `nltk <http://nltk.org/>`_.

To set up quepy to be able to use `nltk <http://nltk.org/>`_ type:

::

    $ quepy nltkdata /some/path/you/find/convenient

Also, every time you start a new app or use one, like the dbpedia example,
you should configure `settings.py` to point to the path you chose.
