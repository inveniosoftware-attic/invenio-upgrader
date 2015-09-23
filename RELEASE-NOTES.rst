=========================
 Invenio-Upgrader v0.1.2
=========================

Invenio-Upgrader v0.1.2 was released on September 23, 2015.

About
-----

Upgrader engine for Invenio modules.

*This is an experimental developer preview release.*

Bug fixes
---------

- Removes dependencies to invenio.testsuite and replaces them with
  invenio_testing.
- Removes dependencies to invenio.utils and replaces them with
  invenio_utils.
- Removes dependencies to invenio.ext and replaces them with
  invenio_ext.
- Removes calls to PluginManager consider_setuptools_entrypoints()
  removed in PyTest 2.8.0.
- Runs the sql statement which actually changes the engine from MyISAM
  to InnoDB.
- Upgrades pinned alembic version to allow the usage of
  `batch_alter_table` method.
- Adds missing `invenio_base` dependency.

Installation
------------

   $ pip install invenio-upgrader==0.1.2

Documentation
-------------

   http://invenio-upgrader.readthedocs.org/en/v0.1.2

Happy hacking and thanks for flying Invenio-Upgrader.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/invenio-upgrader
|   URL: http://invenio-software.org
