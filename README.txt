Introduction
============

``Parse to Plone`` is an lxml/soup parser (in the form of a Buildout recipe) to 
easily get content from static HTML files into Plone.

Install
-------

You can install ``Parse to Plone`` by editing your buildout.cfg file as
follows.

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

Use ``--ignore`` to specify the number of directories to ignore.

Example #1
----------

If you have a site in /var/www/html that contains the following::

    /var/www/html/index.html
    /var/www/html/about/index.html

You should run::

    $ bin/plone run bin/import /var/www/html --ignore=3

('var', 'www', and 'html' are the three directories to ignore)

This will import ``index.html`` and ``about/index.html``.

Example #2
----------

If you have a site in ../client-site that contains the following::

    ../client-site/index.html
    ../client-site/about/index.html

You should run::

    $ bin/plone run bin/import ../client-site --ignore=2

('..', and 'client-site' are the two directories to ignore)

This will import ``index.html`` and ``about/index.html``.

Help
----

Questions/comments/concerns? Email: aclark@aclark.net

