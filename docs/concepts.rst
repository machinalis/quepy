Important Concepts
==================

Part of Speech tagset
---------------------

The POS tagset used by quepy it's the **Penn Tagset** as defined
`here <http://www.comp.leeds.ac.uk/ccalas/tagsets/upenn.html>`_.

Keywords
--------

When doing queries to a database it's very common to have a unified way to obtain
data from it. In quepy we called it keyword.
To use the Keywords in a quepy project you must first configurate what's the
relationship that you're using. You do this by defining the class attribute
of the :class:`quepy.dsl.HasKeyword`.

For example, if you want to use **rdfs:label** as Keyword relationship you do:

.. code-block:: python

    from quepy.dsl import HasKeyword
    HasKeyword.relation = "rdfs:label"

If your Keyword uses language specification you can configure this by doing:

.. code-block:: python

    HasKeyword.language = "en"

Quepy provides some utils to work with Keywords, like
:func:`quepy.dsl.handle_keywords`. This function will take some
text and extract IRkeys from it. If you need to define some sanitize
function to be applied to the extracted Keywords, you have define the
`staticmethod` sanitize. 

For example, if your IRkeys are always in lowercase, you can define:

.. code-block:: python

    HasKeyword.sanitize = staticmethod(lambda x: x.lower())


Particles
---------

It's very common to find patterns that are repeated on several regex so quepy
provides a mechanism to do this easily. For example, in the DBpedia example,
a country it's used several times as regex and it has always the same interpretation.
In order to do this in a clean way, one can define a Particle by doing:

.. code-block:: python

    class Country(Particle):
        regex = Plus(Pos("NN") | Pos("NNP"))

        def interpret(self, match):
            name = match.words.tokens.title()
            return IsCountry() + HasKeyword(name)

this 'particle' can be used to match thing in regex like this:

.. code-block:: python

    regex = Lemma("who") + Token("is") + Pos("DT") + Lemma("president") + \
        Pos("IN") + Country() + Question(Pos("."))


and can be used in the interpret() method just as an attribut of the match object:

.. code-block:: python

    def interpret(self, match):
        president = PresidentOf(match.country)
