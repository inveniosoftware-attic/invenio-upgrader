..
    This file is part of Invenio.
    Copyright (C) 2015 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

Changes
=======

Version 0.2.0 (release 2015-10-05)
----------------------------------

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Removes legacy upgrade recipes. You **MUST** upgrade to the latest
  Invenio 2.1 before upgrading Invenio-Upgrader. (#14)

Version 0.1.2 (release 2015-09-23)
----------------------------------

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

Version 0.1.1 (release 2015-09-07)
----------------------------------

- Replaces usage of invenio.config with flask current_app.config.

Version 0.1.0 (release 2015-08-19)
----------------------------------

- Initial public release.
