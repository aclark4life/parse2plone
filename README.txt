Introduction
============

``Parse2Plone`` is an lxml/soup parser (in the form of a Buildout recipe) to 
easily get content from static HTML files into Plone.

Installation
------------

You can install ``Parse2Plone`` by editing your *buildout.cfg* file like
so:

- First, add an ``import`` section::

    [import]
    recipe = parse2plone

- Then, add the ``import`` section to the list of parts::

    [buildout]
    …
    parts =
        …
        import

- Now run ``bin/buildout`` as usual.

Execution
---------

You can run ``Parse2Plone`` like so::

    $ bin/plone run bin/import /path/to/files

Demonstration
-------------

If you have a site in /var/www/html that contains the following::

    /var/www/html/index.html
    /var/www/html/about/index.html

You should run::

    $ bin/plone run bin/import /var/www/html

And the following will be created:

    - http://localhost:8080/Plone/index.html
    - http://localhost:8080/Plone/about/index.html

Explanation
-----------

Why did you create ``Parse2Plone`` when the following packages (and probably many
more) already exist:

    - http://pypi.python.org/pypi/collective.transmogrifier
        - http://pypi.python.org/pypi/transmogrify.filesystem
        - http://pypi.python.org/pypi/transmogrify.htmlcontentextractor

Here are a few reasons:

- Because ``Parse2Plone`` is aimed at lowering the bar. Particularly for folks
  that don't know (or want to know) what a "transmogrifier blueprint" is, but
  can edit their *buildout.cfg* files and run a single command without having
  to think too much.

- collective.transmogrify provides a framework for creating reusable pipes
  (whose definitions are called blueprints). ``Parse2Plone`` only provides 
  a single, non-reusable "pipe/blueprint".

- The author had an itch to scratch. It wil be nice for him to able to say 
  "just write a script" and then actually be able to point to an example.

Consternation
-------------

``Parse2Plone`` requires ``lxml`` which in turn requires ``libxml2`` and
``libxslt``. If you do not have ``lxml`` installed "globally" (i.e. in your
system Python's site-packages directory) then Buildout will try to install it
for you.

At this point ``lxml`` will look for the libxml2/libxslt2 development
libraries to build against, and if you don't have them installed on your system
already *your mileage
may vary* (i.e. Buildout will fail).

Communication
-------------

Questions, comments, or concerns? Email: aclark@aclark.net
