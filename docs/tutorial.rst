Application Tutorial
====================

.. Note::

    The aim of this tutorial is to show you how to build a custom natural
    language interface to your own database using an example.

To illustrate how to use quepy as a framework for natural language interface
for databases, we will build (step by step) an example application to access
`DBpedia <http://dbpedia.org/>`_.

The finished example application can be tried online here:
`Online demo <http://quepy.machinalis.com/>`_

The finished example code can be found here:
`Code <https://github.com/machinalis/quepy/tree/master/examples/dbpedia/dbpedia>`_

The first step is to select the questions that we want to be answered with
dbpedia's database and then we will develop the quepy machinery to transform
them into SPARQL queries.

Selected Questions
------------------

In our example application, we'll be seeking to answer questions like:

Who is *<someone>*, for example:

* Who is Tom Cruise?
* Who is President Obama?

What is *<something>*, for example:

* What is a car?
* What is the Python programming language?

List *<brand>* *<something>*, for example:

* List Microsoft software
* List Fiat cars

Starting a quepy project
------------------------

To start a quepy project, you must create a quepy application.  In our
example, our application is called `dbpedia`, and we create the
application by running:

::

    $ quepy startapp dbpedia


You'll find out that a folder and some files were created.
It should look like this:

::

    $ cd dbpedia
    $ tree .

    .
    ├── dbpedia
    │   ├── __init__.py
    │   ├── basic.py
    │   ├── dsl.py
    │   └── settings.py
    └── main.py

    1 directory, 4 files

This is the basic structure of every quepy project.

* `dbpedia/basic.py`: the file where you will define the regular expressions
  that will match natural language questions and transform them into an
  abstract semantic representation.
* `dbpedia/dsl.py`: the file where you will define the domain specific language
  of your database schema. In the case of SPARQL, here you will be specifying
  things that usually go in the ontology: relation names and such.
* `dbpedia/settings.py`: the configuration file for some aspects of the
  installation.
* `main.py`: this file is an optional kickstart point where you can have all the
  code you need to interact with your app. If you want, you can safely remove
  this file.

.. _configuring-application:

Configuring the application
---------------------------

First make sure you have already downloaded the necessary
data for the `nltk tagger <http://nltk.org/>`_. If not check the
:doc:`installation section. <installation>`

Now edit *dbpedia/settings.py* and add the path to the nltk data to the
`NLTK_DATA` variable.
This file has some other configuration options, but we are not going to need
them for this example.

Also configure the `LANGUAGE`, in this example we'll use ``sparql``.

.. Note::
    
    What's a tagger anyway?

    A "tagger" (in this context) is a linguistic tool help analyze natural
    language. It's composed of:

        - `A tokenizer <http://en.wikipedia.org/wiki/Tokenization>`_
        - `A part-of-speech tagger <http://en.wikipedia.org/wiki/Part-of-speech_tagging>`_
        - `A lemmatizer <http://en.wikipedia.org/wiki/Lemmatisation>`_

    If this is too much info for you, you can just treat it like a black box
    and it will be enough in the Quepy context.


Defining the regex
------------------

.. Note::

    To handle regular expressions, quepy uses `refo <https://github.com/machinalis/refo>`_, an awesome library to work with regular expressions as objects.
    You can read more about refo `here <https://github.com/machinalis/refo>`_.

We need to define the regular expressions that will match natural
language questions and transform them into an abstract semantic
representation. This will define specifically which questions the
system will be able to handle and *what* to do with them.

In our example, we'll be editing the file *dbpedia/basic.py*. Let's
look at an example of regular expression to handle *"What is ..."*
questions. The whole definition would look like this:

.. code-block:: python
    :linenos:

    from refo import Group, Question
    from quepy.dsl import HasKeyword
    from quepy.parsing import Lemma, Pos, QuestionTemplate

    from dsl import IsDefinedIn

    class WhatIs(QuestionTemplate):
        """
        Regex for questions like "What is ..."
        Ex: "What is a car"
        """

        target = Question(Pos("DT")) + Group(Pos("NN"), "target")
        regex = Lemma("what") + Lemma("be") + target + Question(Pos("."))

        def interpret(self, match):
            thing = match.target.tokens
            target = HasKeyword(thing)
            definition = IsDefinedIn(target)
            return definition


Now let's discuss this procedure step by step.

First of all, note that regex handlers need to be a subclass from
:class:`quepy.parsing.QuestionTemplate`. They also need to define a class
attribute called ``regex`` with a refo regex.

Then, we describe the structure of the input question as a regular expression,
and store it in the *regex* attribute. In our example, this is done in Line 14:

.. code-block:: python

    regex = Lemma("what") + Lemma("be") + target + Question(Pos("."))

This regular expression matches questions of the form "what is X?",
but also "what was X?", "what were X?" and other variants of the verb
to be because it is using the *lemma* of the verb in the regular
expression. Note that the X in the question is defined by a variable
called *target*, that is defined in Line 13:

.. code-block:: python

    target = Question(Pos("DT")) + Group(Pos("NN"), "target")

The *target* variable matches a string that will be passed on to the
semantics to make part of the final query. In this example, we define
that we want to match optionally a determiner (DT) followed by a noun
(NN) labeled as "target".

Note that quepy can access different levels of linguistic information
associated to the words in a question, namely their lemma and part of
speech tag. This information needs to be associated to questions by
analyzing them with a tagger.

Finally, if a regex has a successful match with an input question, the
``interpret`` method will be called with the match. In Lines 16 to 22,
we define the *interpret* method, which specifies the semantics of a
matched question:

.. code-block:: python

    def interpret(self, match):
        thing = match.target.tokens
        target = HasKeyword(thing)
        definition = IsDefinedIn(target)
        return definition

In this example, the contents of the target variable are the argument
of a `HasKeyword` predicate. The `HasKeyword` predicate is part of the
vocabulary of our specific database. In contrast, the `IsDefinedIn`
predicate is part of the abstract semantics component that is
described in the next section.


Defining the domain specific language
-------------------------------------

Quepy uses an abstract semantics as a language-independent
representation that is then mapped to a query language. This allows
your questions to be mapped to different query languages in a
transparent manner.

In our example, the domain specific language is defined in the file
*dbpedia/dsl.py*.

Let's see an example of the dsl definition. The predicate `IsDefinedIn`
was used in line 21 of the previous example:

.. code-block:: python

    definition = IsDefinedIn(target)

`IsDefinedIn` is defined in the `dsl.py` file as follows:

.. code-block:: python

    from quepy.dsl import FixedRelation

    class IsDefinedIn(FixedRelation):
        relation = "rdfs:comment"
        reverse = True

This means that `IsDefinedIn` is a Relation where the subject has
`rdf:comment`. By creating a quepy class, we provide a further level of
abstraction on this feature which allows to integrate it in regular
expressions seamlessly.

The ``reverse`` part of the deal it's not easy to explain, so bear with me.
When we say ``relation = "rdfs:comment"`` and ``definition = IsDefinedIn(target)``
we are stating that we want

::

    ?target rdfs:comment ?definition

But how does the framework knows that we are not trying to say this?:

::

    ?definition rdfs:comment ?target

Well, that's where ``reverse`` kicks in. If you set it to ``True`` (it's
``False`` by default) you get the first situation, if not you get the second
situation.


Using the application
---------------------

With all that set, we can now use our application. In the *main.py* file of
our example there are some lines of code to use the application.

.. code-block:: python

    import quepy
    dbpedia = quepy.install("dbpedia")
    target, query, metadata = dbpedia.get_query("what is a blowtorch?")
    print query


This code should be enough to obtain the following query:

::

    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX quepy: <http://www.machinalis.com/quepy#>

    SELECT DISTINCT ?x1 WHERE {
      ?x0 quepy:Keyword "blowtorch".
      ?x0 rdfs:comment ?x1.
    }
