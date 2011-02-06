.. contents:: :depth: 2

mr.importer
===========

Easily import static websites on the file system into Plone via a command
like::

    $ bin/plone run bin/import /path/to/files

Introduction
------------

``mr.importer`` is a Buildout recipe that creates a script for you to easily
get content from static HTML websites on the file system into Plone.

Warning
-------

This is a **Buildout** recipe for use with **Plone**; by itself it does nothing. If you
don't know what Plone is, please see: http://plone.org. If you don't know
what Buildout is, please see: http://www.buildout.org/.

Getting started
---------------

First, a couple caveats:

* A Plone site object must exist in the Zope2 instance database. By default in mr.importer,
  that site object is assumed to be named "Plone".

* An admin user must exist in the Zope2 instance database (or Plone site). By
  default in mr.importer that user is assumed to be named "admin".

And because it drives the author nuts whenever he has to dig for a recipe's options,
here are this recipe's options with sample values::

    [import]
    recipe = mr.importer

    # core features
    path = /Plone
    user = admin
    illegal_chars = _ . +
    illegal_words =
    illegal_expressions =
    html_extensions = html
    image_extensions = png
    file_extensions = mp3
    target_tags = p
   
    # additional features
    force = false
    publish = false
    collapse = false
    create_spreadsheet = false
    replacetypes =
    rename =
    match =
    paths =

.. Note::
    The parameters listed above are configured with their default values. Edit these
    values if you would like to change the default behavior; they are (mostly)
    self-explanatory. Now you can just cut and paste to get started or keep reading if
    you would like to know more.

.. Note::
    This recipe creates a script that is **not** intended to be run directly.
    Due to technical limitations, the author was not able to implement a user
    friendly error message. So if you run ``bin/import`` directly you will see
    this::

        $ bin/import
        Traceback (most recent call last):
          File "bin/import", line 116, in <module>
            mr.importer.main(app=app, path='/Plone', illegal_chars='_,.',
        illegal_words='id,start', illegal_expressions='[0-9]', html_extensions='html',
        image_extensions='gif,jpg,jpeg,png', file_extensions='mp3,xls',
        target_tags='a,div,font,h1,h2,p', force=True, publish=False, collapse=False,
        rename=None, replacetypes=None, match=None, create_spreadsheet=True)
        NameError: name 'app' is not defined

    To avoid this, run the script as intended::

        $ bin/plone run bin/import /path/to/files

    See the `execution`_ section below for more information.

Installation
------------

You can install ``mr.importer`` by editing your ``buildout.cfg`` file like
so. First add an ``import`` section::

    [import]
    recipe = mr.importer

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

Now you can run ``mr.importer`` like this::

    $ bin/plone run bin/import /path/to/files

.. Note:: 
    In the example above and examples below, ``bin/plone`` refers to a *Zope 2
    instance* script created by `plone.recipe.zope2instance`_.

    Your ``bin/plone`` script may be called ``bin/instance`` or
    ``bin/client``, etc. instead.

.. _`plone.recipe.zope2instance`: http://pypi.python.org/pypi/plone.recipe.zope2instance

Example
-------

If you have a site in /var/www/html that contains the following::

    /var/www/html/index.html
    /var/www/html/about/index.html

You should run::

    $ bin/plone run bin/import /var/www/html

And the following will be created:

* http://localhost:8080/Plone/index.html
* http://localhost:8080/Plone/about/index.html

Customization
-------------

Modifying the default behavior of ``mr.importer`` is easy; just use the command
line options or add parameters to your ``buildout.cfg`` file. Both approaches
allow customization of the exact same set of options, but the command line
arguments will trump any settings found in your ``buildout.cfg`` file.

Buildout options
~~~~~~~~~~~~~~~~

You can configure the following parameters in your ``buildout.cfg`` file in
the ``mr.importer`` recipe section.

Options
'''''''
+----------------------+------------+----------------------------------------+
| **Parameter**        |**Default** | **Description**                        |
|                      |**value**   |                                        |
+----------------------+------------+----------------------------------------+
| ``path``             |/Plone      | Specify an alternate location in the   |
|                      |            | database for the import to occur.      |
+----------------------+------------+----------------------------------------+
| ``user``             |admin       | Specify an alternate user to import    |
|                      |            | content with.                          |
+----------------------+------------+----------------------------------------+
| ``illegal_chars``    |_ .         | Specify illegal characters.            |
|                      |            | ``mr.importer`` will ignore files that |
|                      |            | contain these characters.              |
+----------------------+------------+----------------------------------------+
| ``html_extensions``  |html        | Specify HTML file extensions.          |
|                      |            | ``mr.importer`` will import HTML files |
|                      |            | with these extensions                  |
+----------------------+------------+----------------------------------------+
| ``image_extensions`` |png, gif,   | Specify image file extensions.         |
|                      |jpg, jpeg,  | ``mr.importer`` will import image files|
|                      |            | with these extensions.                 |
+----------------------+------------+----------------------------------------+
| ``file_extensions``  |mp3, xls    | Specify image file extensions.         |
|                      |            | ``mr.importer`` will import files with |
|                      |            | with these extensions as files in Plone|
|                      |            | (unless you configure                  |
|                      |            | create_spreadsheet=true, see below)    |
+----------------------+------------+----------------------------------------+
| ``target_tags``      |a h1 h2 p   | Specify target tags. ``mr.importer``   |
|                      |            | will parse the contents of HTML tags   |
|                      |            | listed. If any tag is provided as an   |
|                      |            | XPath expression (any expression       |
|                      |            | begining with /) the matching elements |
|                      |            | will first be extracted from the root  |
|                      |            | document.  Selections for the contents |
|                      |            | of other tags will then be performed   |
|                      |            | only on the document subset.           |
|                      |            | If only XPath expressions are given,   |
|                      |            | then the entire subtree of the matched |
|                      |            | elements are returned (including HTML) |
+----------------------+------------+----------------------------------------+
| ``force``            |false       | Force create folders that do not exist.|
|                      |            | For example, if you do                 |
|                      |            | --path=/Plone/foo and foo does not     |
|                      |            | exist, you will get an error message.  |
|                      |            | Use --force to tell ``mr.importer`` to |
|                      |            | create it.                             |
+----------------------+------------+----------------------------------------+
| ``publish``          |false       | Publish newly created content.         |
+----------------------+------------+----------------------------------------+
| ``collapse``         |false       | "collapse" content. (see               |
|                      |            | collapse_parts() in mr.importer.py)    |
+----------------------+------------+----------------------------------------+
| ``rename``           |            | Rename content. (see rename_parts()    |
|                      |            | in mr.importer.py                      | 
+----------------------+------------+----------------------------------------+
| ``replacetypes``     |            | Use custom types. (see replace_types())|
+----------------------+------------+----------------------------------------+
| ``match``            |            | Match files. (see match_files())       |
+----------------------+------------+----------------------------------------+
| ``paths``            |            | Specify a series of locations on the   |
|                      |            | filesystem, with corresponding         |
|                      |            | locations in the database for imports, |
|                      |            | with syntax:                           |
|                      |            | --paths=import_dirs:object_paths       |
|                      |            | (--path will be ignored)               |
+----------------------+------------+----------------------------------------+
|``create_spreadsheet``| false      | Create "spreadsheets". (see            |
|                      |            | create_spreadsheet() in mr.importer.py)|
+----------------------+------------+----------------------------------------+

Example
'''''''

Instead of accepting the default ``mr.importer`` behaviour, in your
``buildout.cfg`` file you may specify the following::

    [import]
    recipe = mr.importer
    path = /Plone/foo
    html_extensions = htm
    image_extensions = png
    target_tags = p

This will configure ``mr.importer`` to (only) import content from:

* Images ending in ``.png``
* HTML files ending in ``.htm``
* Text within ``p`` tags

*to*: 

* A folder named ``/Plone/foo``.

Command line options
~~~~~~~~~~~~~~~~~~~~

The following ``mr.importer`` command line options are supported.

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

``'--collapse'``
****************

"collapse" content (see collapse_parts() in mr.importer.py).

``'--rename'``
***************

Rename content (see rename_files()).

``'--replacetypes'``
********************

Customize types (see replace_types() in mr.importer.py).

``'--match'``
****************

Match files (see match_files() mr.importer.py).

``'--paths'``
*************

You can specify a series of import paths and corresponding object paths::

    $ bin/plone run bin/import --paths=sample:Plone/sample,sample2:Plone/sample2

``'--create-spreadsheet'``
**************************

You can optionally tell ``mr.importer`` to try and import the contents of any
spreadsheets it finds, by doing this::

    $ bin/plone run bin/import --create-spreadsheet /var/www/html

If /var/www/html/foo.xls exists and has content, then a 
http://localhost:8080/Plone/foo will be created as a page, with the contents
of the spreadsheet in an HTML table.

``'--help'``
************

And lastly, you can always ask ``mr.importer`` to tell you about its available options with
the ``--help`` or ``-h`` option::

    $ bin/plone run bin/import -h

Example
'''''''

Instead of accepting the default ``mr.importer`` behaviour, on the command line you
may specify the following::

    $ bin/plone run bin/import /path/to/files -p /Plone/foo --html-extensions=html \
        --image-extensions=png --target-tags=p

This will configure ``mr.importer`` to (only) import content from:

* Images ending in ``.png``
* HTML files ending in ``.htm``
* Text within ``p`` tags

*to*: 

* A Plone site folder named ``/Plone/foo``.

Troubleshooting
---------------

Here are some trouble-shooting comments/tips.

Compiling lxml
~~~~~~~~~~~~~~

``mr.importer`` requires ``lxml`` which in turn requires ``libxml2`` and
``libxslt``. If you do not have ``lxml`` installed "globally" (i.e. in your
system Python's site-packages directory) then Buildout will try to install it
for you. At this point ``lxml`` will look for the libxml2/libxslt2 development
libraries to build against, and if you don't have them installed on your system
already *your mileage may vary* (i.e. Buildout will fail).

Database access
~~~~~~~~~~~~~~~

Before running ``mr.importer``, you must either stop your Plone site or
use ZEO. Otherwise ``mr.importer`` will not be able to access the
database.

Contact
-------

Questions, comments, or concerns? Please e-mail: aclark@aclark.net.

Credits
-------

Development sponsored by Radio Free Asia 
