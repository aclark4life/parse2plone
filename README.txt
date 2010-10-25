Introduction
============

``Parse2Plone`` is an HTML parser (in the form of a Buildout recipe that
creates a script for you) to easily get content from static HTML files into Plone.

Warning
-------

This is a **Buildout recipe** for use with Plone. By itself it does nothing. If you
do not know what Plone is, please see: http://plone.org. If you do not know
what Buildout is, please see: http://www.buildout.org/.

Getting started
---------------

Because it always drives me nuts when you have to dig for a recipe's options,
here they are::

    [import]
    recipe = parse2plone
    path = Plone
    html_extensions = html
    image_extensions = gif jpg jpeg png
    target_tags = a div h1 h2 p
    illegal_chars = _ .

The parameters listed are configured with their default values. Edit these if you 
would like to change the default behavior; they are (hopefully) self-explanatory.
Now you can just cut and paste to get started or keep reading if you would like
to know more.

Explanation
-----------

Why did you create ``Parse2Plone`` when the following packages (and probably many
more) already exist:

    - http://pypi.python.org/pypi/collective.transmogrifier
        - http://pypi.python.org/pypi/transmogrify.filesystem
        - http://pypi.python.org/pypi/transmogrify.htmlcontentextractor

Here are a few reasons:

- Because ``Parse2Plone`` is aimed at lowering the bar for folks who don't already
  know (or want to know) what a "transmogrifier blueprint" is but can update
  their ``buildout.cfg`` file, run ``Buildout``, and then run a single import command
  to import static content from the file system all without having to think very much.

- collective.transmogrify provides a framework for creating reusable pipes
  (whose definitions are called blueprints). ``Parse2Plone`` provides 
  a single, non-reusable "pipe/blueprint".

- The author had an itch to scratch; it will be nice for him to be able to say
  "just go write a script" and then point to an example.

Installation
------------

You can install ``Parse2Plone`` by editing your ``buildout.cfg`` file like
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

Modification
------------

Modifying the default behavior of ``parse2plone`` is easy; just use the command
line options or add parameters to your ``buildout.cfg`` file. Both approaches
allow customization of the same set of options, but the command line arguments
will trump any settings found in your ``buildout.cfg`` file. The easiest way
to modify settings is to edit your ``buildout.cfg`` file.

Buildout options
~~~~~~~~~~~~~~~~

You can configure the following parameters in your ``buildout.cfg`` file.

Options
'''''''

- ``path``: Specify an alternate location for the Plone site object in the
  database.
- ``html_extensions``: Specify HTML file extensions. ``parse2plone`` will
  import HTML files with these extensions.
- ``illegal_chars``: Specify illegal characters. ``parse2plone`` will ignore
  files that contain these characters.
- ``image_extensions``: Specify image file extensions. ``parse2plone`` will
  import image files with these extensions.
- ``target_tags``: Specify target tags. ``parse2plone`` will parse the
  contents of HTML tags listed.

Example
'''''''

Instead of accepting the default behaviour in your ``buildout.cfg`` file you
may specify the following::

    ...
    [import]
    recipe = parse2plone
    path = Plone2
    html_extensions = htm
    image_extensions = png
    target_tags = p
    ...

This will configure ``parse2plone`` to (only) import content *from*:

    - Images ending in ``.png``
    - HTML files ending in ``.htm``
    - Text within ``p`` tags

*to*: 

    - A Plone site object named ``Plone2``.

Command line options
~~~~~~~~~~~~~~~~~~~~

The following ``parse2plone`` command line options are supported.

Options
'''''''

Path (``'--path'``, ``'-p'``)
*****************************

You can specify an alternate path to the Plone site object located within
the database ('/Plone' by default) with ``--path`` or ``-p``::

    $ bin/plone run bin/import /path/to/files --path=Plone2
    $ bin/plone run bin/import /path/to/files -p Plone2

HTML file extensions (``'--html-extensions'``)
**********************************************

You can specify HTML file extensions with the ``--html-extensions`` option::

    $ bin/plone run bin/import /path/to/files --html-extensions=htm

Image file extensions (``'--image-extensions'``)
************************************************

You can specify image file extensions with the ``--image-extensions`` option::

    $ bin/plone run bin/import /path/to/files --image-extensions=png

Target tags (``'--target-tags'``)
*********************************

You can specify the target tags to parse with the ``--target-tags`` option::

    $ bin/plone run bin/import /path/to/files --target-tags=p

Example
'''''''

Instead of accepting the default ``parse2plone`` behaviour, on the command line you
may specify the following::

    $ bin/plone run bin/import /path/to/files -p Plone2 --html-extensions=html \
        --image-extensions=png --target-tags=p

This will configure ``parse2plone`` to (only) import content *from*:

    - Images ending in ``.png``
    - HTML files ending in ``.htm``
    - Text within ``p`` tags

*to*: 

    - A Plone site object named ``Plone2``.

Consternation
-------------

Here are some trouble-shooting comments/tips.

Compiling lxml
~~~~~~~~~~~~~~

``Parse2Plone`` requires ``lxml`` which in turn requires ``libxml2`` and
``libxslt``. If you do not have ``lxml`` installed "globally" (i.e. in your
system Python's site-packages directory) then Buildout will try to install it
for you. At this point ``lxml`` will look for the libxml2/libxslt2 development
libraries to build against, and if you don't have them installed on your system
already *your mileage may vary* (i.e. Buildout will fail).

Database access
~~~~~~~~~~~~~~~

Before running ``parse2plone``, you must either stop your Plone site or
use ZEO. Otherwise ``parse2plone`` will not be able to access the
database.

Communication
-------------

Questions, comments, or concerns? Email: aclark@aclark.net
