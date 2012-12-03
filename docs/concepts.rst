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
of the :class:`quepy.semantics.HasKeyword`.

For example, if you want to use **rdfs:label** as Keyword relationship you do:

.. code-block:: python

    from quepy.semantics import HasKeyword
    HasKeyword.relation = "rdfs:label"

If your Keyword uses language specification you can configure this by doing:

.. code-block:: python

    HasKeyword.language = "en"

Quepy provides some utils to work with Keywords, like
:func:`quepy.semantic_utils.handle_keywords`. This function will take some
text and extract IRkeys from it. If you need to define some sanitize
function to be applied to the extracted Keywords, you have define the
`staticmethod` sanitize. 

For example, if your IRkeys are always in lowercase, you can define:

.. code-block:: python

    HasKeyword.sanitize = staticmethod(lambda x: x.lower())
