Introduction
============

'Parse to Plone' is my lxml/soup parser.

Install
-------

You can install 'Parse to Plone' with the ``zc.recipe.egg`` recipe like so:

- Add an ``import`` section::

    [import]
    recipe = zc.recipe.egg
    eggs = 
        parse2plone


- Add the ``import`` section to the list of parts::

    [buildout]
    …
    parts =
        …
        import

Run
---

You can run 'Parse to Plone' like so::

    $ bin/plone run bin/import /path/to/files
