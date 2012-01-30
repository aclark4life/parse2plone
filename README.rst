.. contents:: :depth: 2

parse2plone
=====

*(Formerly charm, Formerly mr.importer, formerly parse2plone.)*

Import static websites on the file system into Plone via::

    $ bin/plone run bin/parse2plone /path/to/files

.. Warning::

    This is more of a "toy project" than a "real data migrator". For any
    serious Plone migrations, you may want to consider a
    `collective.transmogrifier`_-based tool e.g. `mr.migrator`_. That is not
    to say you will not find ``parse2plone`` useful as a sample migration script,
    just that you should not expect it to scale to meet any complex needs;
    whereas that is exactly what transmogrifier-based tools are designed to do.

Introduction
------------

``parse2plone`` is a Buildout recipe that creates a script for you to
get content from static websites on the file system into Plone.

.. Note::

    This is a **Buildout** recipe for use with **Plone**; by itself it does nothing. If you
    don't know what Plone is, please see: http://plone.org. If you don't know
    what Buildout is, please see: http://www.buildout.org/.

``parse2plone`` relies on the "run" argument of scripts created by
`plone.recipe.zope2instance`_ to mount and modify the Plone database.

Getting started
---------------

* A ``Plone`` site object must exist in the ``Zope2`` instance database. By
  default, parse2plone assumes the site object is named "Plone".

* A user must exist in the ``Zope2`` instance database (or Plone site). By
  default, parse2plone assumes the user is named "admin".

.. Note::
    This recipe creates a script that is **not** intended to be run directly.
    Due to technical limitations, the author was not able to implement a user
    friendly error message. So if you run ``bin/parse2plone`` directly you will see
    this::

        $ bin/parse2plone
        Traceback (most recent call last):
          File "bin/parse2plone", line 117, in <module>
            parse2plone.main(app=app)
        NameError: name 'app' is not defined

    To avoid this, run the script as intended::

        $ bin/plone run bin/parse2plone /path/to/files

    See the `execution`_ section below for more information.

Installation
------------

You can install ``parse2plone`` by editing your ``buildout.cfg`` file like
so::

    [buildout]
    ...
    parts =
        ...
        parse2plone

    [parse2plone]
    recipe = parse2plone

Now run ``bin/buildout`` as usual.

Execution
---------

Now you can run ``parse2plone`` like this::

    $ bin/plone run bin/parse2plone /path/to/files

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

    $ bin/plone run bin/parse2plone /var/www/html

And the following will be created:

* http://localhost:8080/Plone/index.html
* http://localhost:8080/Plone/about/index.html

Troubleshooting
---------------

Here are some trouble-shooting comments/tips.

Compiling lxml
~~~~~~~~~~~~~~

``parse2plone`` requires ``lxml`` which in turn requires ``libxml2`` and
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

Contact
-------

Questions/comments/concerns? Please e-mail: aclark@aclark.net.

Credits
-------

Development sponsored by Radio Free Asia

.. _`collective.transmogrifier`: http://pypi.python.org/pypi/collective.transmogrifier/
.. _`mr.migrator`: https://github.com/collective/mr.migrator

