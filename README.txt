Introduction
============

``Parse to Plone`` is my lxml/soup parser (in the form of a Buildout recipe) to 
get content from static HTML files into Plone.

Install
-------

You can install ``Parse to Plone`` in your buildout.cfg like so.

- Add an ``import`` section::

    [import]
    recipe = parse2plone

- Add the ``import`` section to the list of parts::

    [buildout]
    …
    parts =
        …
        import

Run
---

You can run ``Parse to Plone`` like so::

    $ bin/plone run bin/import /path/to/files

