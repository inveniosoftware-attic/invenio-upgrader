# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2012, 2013, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test Invenio Upgrader."""

from __future__ import absolute_import

import pytest
import os
import shutil
import six
import sys
import tempfile

from datetime import date

from invenio_upgrader import UpgradeBase


# class TestInvenioUpgraderRecipe(InvenioTestCase):
#
#     def setUp(self):
#         """
#         Setup a test python package, to test upgrade recipe creation.
#         """
#         self.tmpdir = tempfile.mkdtemp()
#         self.pkg_path = os.path.join(self.tmpdir, 'invenio_upgrader_test')
#         os.makedirs(self.pkg_path)
#         open(os.path.join(self.pkg_path, '__init__.py'), 'a').close()
#         self.pkg_path_mymod = os.path.join(
#             self.tmpdir, 'invenio_upgrader_test/mymod'
#         )
#         os.makedirs(self.pkg_path_mymod)
#
#         open(os.path.join(self.pkg_path, '__init__.py'), 'a').close()
#         open(os.path.join(self.pkg_path_mymod, '__init__.py'), 'a').close()
#
#         sys.path.append(self.tmpdir)
#         import invenio_upgrader_test
#         import invenio_upgrader_test.mymod
#
#     def tearDown(self):
#         """ Remove test package again """
#         sys.path.remove(self.tmpdir)
#         keys = []
#         for m in sys.modules:
#             if m.startswith('invenio_upgrader_test'):
#                 keys.append(m)
#         for k in keys:
#             del sys.modules[k]
#
#         try:
#             import invenio_upgrader_test
#             raise AssertionError("Test package not removed from sys.path")
#         except ImportError:
#             pass
#
#         shutil.rmtree(self.tmpdir)
#
#     def test_create(self):
#         """ Test creation of upgrades """
#         from invenio_upgrader.commands import \
#             cmd_upgrade_create_standard_recipe
#
#         cmd_upgrade_create_standard_recipe(
#             'invenio_upgrader_test.mymod',
#             depends_on=['test1', 'test2']
#         )
#
#         # Test if upgrade can be imported
#         expexted_name = "mymod_%s_rename_me" % \
#             date.today().strftime("%Y_%m_%d")
#
#         import invenio_upgrader_test.mymod.upgrades
#         upgrade = getattr(
#             __import__(
#                 'invenio_upgrader_test.mymod.upgrades',
#                 globals(), locals(), [expexted_name], -1
#             ),
#             expexted_name
#         )
#         # Test API of created upgrade recipe
#         assert upgrade.depends_on == ['test1', 'test2']
#         assert upgrade.estimate() == 1
#         assert isinstance(upgrade.info(), six.string_types)
#         upgrade.pre_upgrade()
#         upgrade.do_upgrade()
#         upgrade.post_upgrade()
#
#     def test_create_load_engine(self):
#         """ Test creation and loading of upgrades with engine """
#         from invenio_upgrader.commands import \
#             cmd_upgrade_create_standard_recipe
#
#         cmd_upgrade_create_standard_recipe(
#             'invenio_upgrader_test',
#             depends_on=[]
#         )
#
#         expexted_name = "invenio_upgrader_test_%s_rename_me" % \
#             date.today().strftime("%Y_%m_%d")
#
#         # Test if upgrade can be found from the Upgrade
#         from invenio_upgrader.engine import InvenioUpgrader
#         eng = InvenioUpgrader(packages=['invenio_upgrader_test'])
#         upgrades = eng.get_upgrades(remove_applied=False)
#         assert len(upgrades) == 1
#         assert upgrades[0]['id'] == expexted_name
#         assert upgrades[0]['repository'] == 'invenio_upgrader_test'
#
#     def test_double_create(self):
#         """ Test creation of upgrades """
#         from invenio_upgrader.commands import \
#             cmd_upgrade_create_standard_recipe
#
#         cmd_upgrade_create_standard_recipe('invenio_upgrader_test')
#         # Second call fails since module already exists, and we didn't
#         # rename it yet.
#         self.assertRaises(
#             SystemExit,
#             cmd_upgrade_create_standard_recipe,
#             'invenio_upgrader_test',
#         )
#
#     def test_create_with_module(self):
#         from invenio_upgrader.commands import \
#             cmd_upgrade_create_standard_recipe
#
#         # Module instead of package
#         self.assertRaises(
#             SystemExit,
#             cmd_upgrade_create_standard_recipe,
#             'invenio_upgrader.engine'
#         )
#
#     def test_invalid_path(self):
#         """ Test creation of upgrades """
#         from invenio_upgrader.commands import \
#             cmd_upgrade_create_standard_recipe
#
#         self.assertRaises(
#             SystemExit,
#             cmd_upgrade_create_standard_recipe,
#             'invenio_upgrader_test',
#             output_path=os.path.join(self.tmpdir, 'this_does_not_exists')
#         )
#
#     def test_create_release(self):
#         """ Test creation of upgrades """
#         from invenio_upgrader.engine import InvenioUpgrader
#         from invenio_upgrader.commands import \
#             cmd_upgrade_create_standard_recipe, \
#             cmd_upgrade_create_release_recipe
#
#         engine = InvenioUpgrader(packages=[
#             'invenio_upgrader_test', 'invenio_upgrader_test.mymod'])
#
#         cmd_upgrade_create_standard_recipe(
#             'invenio_upgrader_test', depends_on=[]
#         )
#         cmd_upgrade_create_standard_recipe(
#             'invenio_upgrader_test.mymod', depends_on=[]
#         )
#
#         cmd_upgrade_create_release_recipe(
#             'invenio_upgrader_test', repository='invenio', upgrader=engine
#         )
#
#         # Find all endpoints in all repositories
#         upgrades = engine.get_upgrades(remove_applied=False)
#         for u in upgrades:
#             if u['id'] == 'invenio_release_x_y_z':
#                 assert len(u['depends_on']) == 2
