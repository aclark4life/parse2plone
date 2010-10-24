Introduction
============

``Parse2Plone`` is an lxml/soup parser (in the form of a Buildout recipe) to 
easily get content from static HTML files into Plone.

Getting started
---------------

Because it always drives me nuts when you have to dig for a recipe's options,
here they are::

    [import]
    recipe = parse2plone
    #path = Plone
    #html_file_ext = html
    #image_file_ext = gif jpg jpeg png
    #target_tags = a div h1 h2 p
    #illegal_chars = _

Everything but the ``recipe`` parameter is commented out; the parameters
listed are configured with default values. Uncomment/edit these if you 
would like to change the default behavior, they are (hopefully) self-explanatory.
Now you can just cut and paste to get started, or keep reading if you would like to know more.

Installation
------------

You can install ``Parse2Plone`` by editing your *buildout.cfg* file like
so:

- First, add an ``import`` section::

    [import]
    recipe = parse2plone

- Then, add the ``import`` section to the list of parts::

    [buildout]
    ...
    parts =
        ...
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

lxml
~~~~

``Parse2Plone`` requires ``lxml`` which in turn requires ``libxml2`` and
``libxslt``. If you do not have ``lxml`` installed "globally" (i.e. in your
system Python's site-packages directory) then Buildout will try to install it
for you.

At this point ``lxml`` will look for the libxml2/libxslt2 development
libraries to build against, and if you don't have them installed on your system
already *your mileage
may vary* (i.e. Buildout will fail).

Database access
~~~~~~~~~~~~~~~

Before running ``parse2plone``, you must either stop your Plone site or
use ZEO. Otherwise ``parse2plone`` will not be able to access the
database.

Modification
------------

Modifying the default behavior of ``parse2plone`` is easy; use the command
line options or add parameters to your ``buildout.cfg`` file.

Both approaches allow customization of the same set of options, but the
command line arguments will trump any settings found in your ``buildout.cfg`` file.

Command line
~~~~~~~~~~~~

The following ``parse2plone`` command line options are available.

Path (``--path``, ``-p``)
'''''''''''''''''''''''''

You can specify an alternate path to the Plone site object located within
the database ('/Plone' by default) with ``--path`` or ``-p``::

    $ bin/plone run bin/import /path/to/files --path=/path/to/Plone
    $ bin/plone run bin/import /path/to/files -p MyPloneSite

Buildout
~~~~~~~~

The following ``parse2plone`` recipe options are available.

Parameters
''''''''''

You can configure the following parameters in your ``buildout.cfg`` file: 

- ``path`` - Specify an alternate location for the Plone site object in the
  database.
- ``html_file_ext`` - Specify HTML file extensions. ``parse2plone`` will
  import HTML files with these extensions.
- ``illegal_chars`` - Specify illegal characters. ``parse2plone`` will ignore
  files that contain these characters.
- ``image_file_ext`` - Specify image file extensions. ``parse2plone`` will
  import image files with these extensions.
- ``target_tags`` - Specify target tags. ``parse2plone`` will parse the
  contents of HTML tags listed.

Example
'''''''

Instead of accepting the default behaviour, in your ``buildout.cfg`` file you
may specify the following configuration::

    [import]
    recipe = parse2plone
    path = Plone2
    html_file_ext = htm
    image_file_ext = png
    target_tags = p

This will configure ``parse2plone`` to (only) import images ending in
``.png``, and content in ``p`` tags from files ending in ``.htm`` to a Plone
site object named ``Plone2``.

Communication
-------------

Questions, comments, or concerns? Email: aclark@aclark.net
