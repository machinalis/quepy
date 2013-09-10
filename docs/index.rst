.. Quepy documentation master file, created by
   sphinx-quickstart on Mon Nov  5 14:12:47 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Quepy's documentation!
=================================

::                              

    __ _ _   _  ___ _ __  _   _
   / _` | | | |/ _ \ '_ \| | | |
  | (_| | |_| |  __/ |_) | |_| |
   \__, |\__,_|\___| .__/ \__, |
      |_|          |_|    |___/


What's quepy?
=============

Quepy is a python framework to transform natural language questions to queries
in a database query language. It can be easily customized to different kinds of
questions in natural language and database queries. So, with little coding you
can build your own system for natural language access to your database.

Currently **Quepy** provides support for
`Sparql <http://www.w3.org/TR/rdf-sparql-query/>`_ and
`MQL <http://www.freebase.com/>`_
query languages. 
We plan to extended it to other database query languages.


Community
=========

* Email us to ``quepyproject@machinalis.com``
* Join our `mailing list <http://groups.google.com/group/quepy>`_


An example
==========

To illustrate what can you do with quepy, we included an example application to
access `DBpedia <http://dbpedia.org/>`_ contents via their `sparql` endpoint.

You can try the example online here: `Online demo <http://quepy.machinalis.com/>`_

Or, you can try the example yourself by doing:

::

    python examples/dbpedia/main.py "Who is Tom Cruise?"

And it will output something like this:

.. code-block:: sparql

    SELECT DISTINCT ?x1 WHERE {
        ?x0 rdf:type foaf:Person.
        ?x0 rdfs:label "Tom Cruise"@en.
        ?x0 rdfs:comment ?x1.
    }
    
    Thomas Cruise Mapother IV, widely known as Tom Cruise, is an...

The transformation from natural language to sparql is done by first using a
special form of regular expressions:

.. code-block:: python

    person_name = Group(Plus(Pos("NNP")), "person_name")
    regex = Lemma("who") + Lemma("be") + person_name + Question(Pos("."))

And then using and a convenient way to express semantic relations:

.. code-block:: python

    person = IsPerson() + HasKeyword(person_name)
    definition = DefinitionOf(person)

The rest of the transformation is handled automatically by the framework to
finally produce this sparql:

.. code-block:: sparql

    SELECT DISTINCT ?x1 WHERE {
        ?x0 rdf:type foaf:Person.
        ?x0 rdfs:label "Tom Cruise"@en.
        ?x0 rdfs:comment ?x1.
    }


Using a very similar procedure you could generate and MQL query for the same question
obtaining:

.. code-block:: javascript

    [{
        "/common/topic/description": [{}],
        "/type/object/name": "Tom Cruise",
        "/type/object/type": "/people/person"
    }]



Installation
============

You need to have installed `numpy <http://numpy.scipy.org/>`_.
Other than that, you can just type:

::
    
    pip install quepy

You can get more details on the installation here:

`<http://quepy.readthedocs.org/en/latest/installation.html>`_


Contents
========

.. toctree::
   :maxdepth: 2

   installation
   tutorial
   reference
   concepts

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

