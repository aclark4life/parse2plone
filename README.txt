Introduction
============

``Parse2Plone`` is an HTML parser (in the form of a Buildout recipe that
creates a script for you) to easily get content from static HTML websites
into Plone.

Warning
-------

This is a **Buildout recipe** for use with Plone; by itself it does nothing. If you
do not know what Plone is, please see: http://plone.org. If you do not know
what Buildout is, please see: http://www.buildout.org/.

Getting started
---------------

Because it drives the author nuts whenever he has to dig for a recipe's options,
here are this recipe's options::

    [import]
    recipe = parse2plone

    # core features
    path = /Plone
    illegal_chars = _ .
    html_extensions = html
    image_extensions = gif jpg jpeg png
    file_extensions = mp3
    target_tags = a div h1 h2 p
   
    # additional bells & whistles
    force = false
    publish = false
    slugify = false
    rename =
    typeswap =
    match =

The parameters listed above are configured with their default values. Edit these
values if you would like to change the default behavior; they are (mostly)
self-explanatory. Now you can just cut and paste to get started or keep reading if
you would like to know more.

Explanation
-----------

Why did you create ``Parse2Plone`` when the following packages already exist:

* http://pypi.python.org/pypi/collective.transmogrifier

  * http://pypi.python.org/pypi/transmogrify.filesystem
  * http://pypi.python.org/pypi/transmogrify.htmlcontentextractor
  * http://pypi.python.org/pypi/transmogrify.webcrawler

Here are some reasons:

* Because ``Parse2Plone`` is aimed at lowering the bar for folks who don't already
  know (or want to know) what a "transmogrifier blueprint" is but are able to update
  their ``buildout.cfg`` file; run ``Buildout``; then run a single command all
  without having to think too much.

* collective.transmogrify provides a framework for creating reusable pipes
  (whose definitions are called blueprints). ``Parse2Plone`` provides 
  a single, non-reusable "pipe/blueprint".

* The author had an itch to scratch; it will be nice for him to be able to say
  "just go write a script" and then point to an example.

* Transmogrifier and friends appear to be "developer's tools", while the author wants
  ``Parse2Plone`` to be an "end user's tool".

* ``parse2plone`` in addition to its primary role as a content importer, is
  intended to serve as an educational tool; both for the author and consumer.
  Python coding best practices and how to script tasks in Plone are the aim.
  Forking and pull requests are encouraged.

If you are a developer looking to create repeatable migrations, you probably want to be
using ``collective.transmogrifier``. If you are an end user that just wants to see your
static website in Plone, then you might want to give ``Parse2Plone`` a try.

There is also this user/contributor comment, which captures the author's sentiment::

    Parse2Plone's release was very timely as I need either this or something very
    similar - and while I've no doubt I could make transmogrify do the job, it's a
    lot of work for a one-shot loading of legacy pages.

                                                    -Derek Broughton, Pointer
                                                     Stop Consulting, Inc.

Installation
------------

You can install ``Parse2Plone`` by editing your ``buildout.cfg`` file like
so. First add an ``import`` section::

    [import]
    recipe = parse2plone

Then add the ``import`` section to the list of parts::

    [buildout]
    ...
    parts =
        ...
        import

Now run ``bin/buildout`` as usual.

.. Note::
    The section name ``import`` is arbitrary, you can call it whatever you
    want. Just keep in mind that the section name corresponds directly to the
    script name. In other words, whatever you name the section - that's what
    the script will be called.


Execution
---------

Now you can run ``Parse2Plone`` like this::

    $ bin/plone run bin/import /path/to/files

.. Note:: 
    In the example above and examples below, ``bin/plone`` refers to a *Zope 2
    instance* script created by `plone.recipe.zope2instance`_.

    Your ``bin/plone`` script may be called ``bin/instance`` or
    ``bin/client``, etc. instead.

.. _`plone.recipe.zope2instance`: http://pypi.python.org/pypi/plone.recipe.zope2instance

Demonstration
-------------

If you have a site in /var/www/html that contains the following::

    /var/www/html/index.html
    /var/www/html/about/index.html

You should run::

    $ bin/plone run bin/import /var/www/html

And the following will be created:

* http://localhost:8080/Plone/index.html
* http://localhost:8080/Plone/about/index.html

Modification
------------

Modifying the default behavior of ``parse2plone`` is easy; just use the command
line options or add parameters to your ``buildout.cfg`` file. Both approaches
allow customization of the same set of options, but the command line arguments
will trump any settings found in your ``buildout.cfg`` file.

Buildout options
~~~~~~~~~~~~~~~~

You can configure the following parameters in your ``buildout.cfg`` file in
the ``parse2plone`` recipe section.

Options
'''''''
+---------------------+-------------+----------------------------------------+
| **Parameter**       | **Default** | **Description**                        |
|                     | **value**   |                                        |
+---------------------+-------------+----------------------------------------+
| ``path``            | /Plone      | Specify an alternate location in the   |
|                     |             | database for the import to occur.      |
+---------------------+-------------+----------------------------------------+
| ``illegal_chars``   | _ .         | Specify illegal characters.            |
|                     |             | ``parse2plone`` will ignore files that |
|                     |             | contain these characters.              |
+---------------------+-------------+----------------------------------------+
| ``html_extensions`` | html        | Specify HTML file extensions.          |
|                     |             | ``parse2plone`` will import HTML files |
|                     |             | with these extensions                  |
+---------------------+-------------+----------------------------------------+
| ``image_extensions``| png, gif,   | Specify image file extensions.         |
|                     | jpg, jpeg,  | ``parse2plone`` will import image files|
|                     |             | with these extensions.                 |
+---------------------+-------------+----------------------------------------+
| ``file_extensions`` | mp3         | Specify image file extensions.         |
|                     |             | ``parse2plone`` will import files with |
|                     |             | with these extensions.                 |
+---------------------+-------------+----------------------------------------+
| ``target_tags``     | a h1 h2 p   | Specify target tags. ``parse2plone``   |
|                     |             | will parse the contents of HTML tags   |
|                     |             | listed. If any tag is provided as an   |
|                     |             | XPath expression (any expression       |
|                     |             | begining with /) the matching elements |
|                     |             | will first be extracted from the root  |
|                     |             | document.  Selections for the contents |
|                     |             | of other tags will then be performed   |
|                     |             | only on the document subset.           |
|                     |             | If only XPath expressions are given,   |
|                     |             | then the entire subtree of the matched |
|                     |             | elements are returned (including HTML) |
+---------------------+-------------+----------------------------------------+
| ``force``           | false       | Force create folders that do not exist.|
+---------------------+-------------+----------------------------------------+
| ``publish``         | false       | Publish newly created content.         |
+---------------------+-------------+----------------------------------------+
| ``slugify``         | false       | "Slugify" content. (see slugify.py)    |
+---------------------+-------------+----------------------------------------+
| ``rename``          |             | Rename content. (see rename.py)        |
+---------------------+-------------+----------------------------------------+
| ``typeswap``        |             | Swap types. (see typeswap.py)          |
+---------------------+-------------+----------------------------------------+
| ``match``           |             | Match files. (see match.py)            |
+---------------------+-------------+----------------------------------------+

Example
'''''''

Instead of accepting the default ``parse2plone`` behaviour, in your
``buildout.cfg`` file you may specify the following::

    [import]
    recipe = parse2plone
    path = /Plone/foo
    html_extensions = htm
    image_extensions = png
    target_tags = p

This will configure ``parse2plone`` to (only) import content *from*:

* Images ending in ``.png``
* HTML files ending in ``.htm``
* Text within ``p`` tags

*to*: 

* A folder named ``/Plone/foo``.

Command line options
~~~~~~~~~~~~~~~~~~~~

The following ``parse2plone`` command line options are supported.

Options
'''''''

``'--path'``, ``'-p'``
**********************

You can specify an alternate import path ('/Plone' by default)
with ``--path`` or ``-p``::

    $ bin/plone run bin/import /path/to/files --path=/Plone/foo

``'--html-extensions'``
***********************

You can specify HTML file extensions with the ``--html-extensions`` option::

    $ bin/plone run bin/import /path/to/files --html-extensions=htm

``'--image-extensions'``
************************

You can specify image file extensions with the ``--image-extensions`` option::

    $ bin/plone run bin/import /path/to/files --image-extensions=png

``'--file-extensions'``
***********************

You can specify generic file extensions with the ``--file-extensions`` option::

    $ bin/plone run bin/import /path/to/files --file-extensions=pdf

``'--target-tags'``
*******************

You can specify the target tags to parse with the ``--target-tags`` option::

    $ bin/plone run bin/import /path/to/files --target-tags=p

``'--force'``
*************

Force create folders that do not exist.

``'--publish'``
***************

Publish newly created content.

``'--slugify'``
***************

"Slugify" content (see slugify.py).

``'--rename'``
***************

Rename content (see rename.py).

``'--typeswap'``
****************

Swap types (see typeswap.py).

``'--match'``
****************

Match files (see match.py).

``'--help'``
************

And lastly, you can always ask ``parse2plone`` to tell you about its available options with
the ``--help`` or ``-h`` option::

    $ bin/plone run bin/import -h
    Usage: import [options]

    Options:
      -h, --help            show this help message and exit
      -p PATH, --path=PATH  Path to Plone site object or sub-folder
      --html-extensions=HTML_EXTENSIONS
                            Specify HTML file extensions
      --illegal-chars=ILLEGAL_CHARS
                            Specify characters to ignore
      --image-extensions=IMAGE_EXTENSIONS
                            Specify image file extensions
      --file-extensions=FILE_EXTENSIONS
                            Specify generic file extensions
      --target-tags=TARGET_TAGS
                            Specify HTML tags to parse
      --force               Force creation of folders
      --publish             Optionally publish newly created content
      --slugify             Optionally "slugify" content (see slugify.py)
      --rename=RENAME       Optionally rename content (see rename.py)
      --typeswap=TYPESWAP   Optionally swap content types (see typeswap.py)


Example
'''''''

Instead of accepting the default ``parse2plone`` behaviour, on the command line you
may specify the following::

    $ bin/plone run bin/import /path/to/files -p /Plone/foo --html-extensions=html \
        --image-extensions=png --target-tags=p

This will configure ``parse2plone`` to (only) import content *from*:

* Images ending in ``.png``
* HTML files ending in ``.htm``
* Text within ``p`` tags

*to*: 

* A Plone site folder named ``/Plone/foo``.

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

Questions, comments, or concerns? Please e-mail: aclark@aclark.net.
