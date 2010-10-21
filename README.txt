Introduction
============

``Parse to Plone`` is an lxml/soup parser (in the form of a Buildout recipe) to 
easily get content from static HTML files into Plone.

Installation
------------

You can install ``Parse to Plone`` by editing your buildout.cfg file like
so:

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

You can run ``Parse to Plone`` like this::

    $ bin/plone run bin/import /path/to/files --ignore=3

Example
-------

If you have a site in /var/www/html that contains the following::

    /var/www/html/index.html
    /var/www/html/about/index.html

Run::

    $ bin/plone run bin/import /var/www/html
