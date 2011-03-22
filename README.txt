.. contents:: :depth: 2

charm
=====

*(Formerly mr.importer, formerly parse2plone.)*

Import static websites on the file system into Plone via::

    $ bin/plone run bin/charm /path/to/files

Works like a charm!

.. Warning::

    This is more of a "toy" project than a "real" data migrator. For any
    serious Plone migrations, you may want to consider a
    `collective.transmogrifier`_-based tool e.g. `mr.migrator`_. That is not
    to say you will not find ``charm`` useful as a sample migration script,
    just that you should not expect it to scale to meet any complex needs;
    whereas that is exactly what transmogrifier-based tools are designed to do.

Introduction
------------

``charm`` is a Buildout recipe that creates a script for you to
get content from static websites on the file system into Plone.

.. Note::

    This is a **Buildout** recipe for use with **Plone**; by itself it does nothing. If you
    don't know what Plone is, please see: http://plone.org. If you don't know
    what Buildout is, please see: http://www.buildout.org/.

``charm`` relies on the "run" argument of scripts created by
`plone.recipe.zope2instance`_ to mount and modify the Plone database.

Getting started
---------------

* A ``Plone`` site object must exist in the ``Zope2`` instance database. By
  default, charm assumes the site object is named "Plone".

* A user must exist in the ``Zope2`` instance database (or Plone site). By
  default, charm assumes the user is named "admin".

.. Note::
    This recipe creates a script that is **not** intended to be run directly.
    Due to technical limitations, the author was not able to implement a user
    friendly error message. So if you run ``bin/charm`` directly you will see
    this::

        $ bin/charm
        Traceback (most recent call last):
          File "bin/charm", line 117, in <module>
            charm.main(app=app)
        NameError: name 'app' is not defined

    To avoid this, run the script as intended::

        $ bin/plone run bin/charm /path/to/files

    See the `execution`_ section below for more information.

Installation
------------

You can install ``charm`` by editing your ``buildout.cfg`` file like
so::

    [buildout]
    ...
    parts =
        ...
        charm

    [charm]
    recipe = charm

Now run ``bin/buildout`` as usual.

Execution
---------

Now you can run ``charm`` like this::

    $ bin/plone run bin/charm /path/to/files

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

    $ bin/plone run bin/charm /var/www/html

And the following will be created:

* http://localhost:8080/Plone/index.html
* http://localhost:8080/Plone/about/index.html

Troubleshooting
---------------

Here are some trouble-shooting comments/tips.

Compiling lxml
~~~~~~~~~~~~~~

``charm`` requires ``lxml`` which in turn requires ``libxml2`` and
``libxslt``. If you do not have ``lxml`` installed "globally" (i.e. in your
system Python's site-packages directory) then Buildout will try to install it
for you. At this point ``lxml`` will look for the libxml2/libxslt2 development
libraries to build against, and if you don't have them installed on your system
already *your mileage may vary* (i.e. Buildout will fail).

Database access
~~~~~~~~~~~~~~~

Before running ``charm``, you must either stop your Plone site or
use ZEO. Otherwise ``charm`` will not be able to access the
database.

Contact
-------

Questions/comments/concerns? Please e-mail: aclark@aclark.net.

Credits
-------

Development sponsored by Radio Free Asia

.. _`collective.transmogrifier`: http://pypi.python.org/pypi/collective.transmogrifier/
.. _`mr.migrator`: https://github.com/collective/mr.migrator

