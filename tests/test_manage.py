# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2015 CERN.
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

"""Unit tests for the inveniomanage script."""

from __future__ import print_function

from invenio_base.utils import run_py_func

from invenio_testing import InvenioTestCase


class UpgraderManageTest(InvenioTestCase):

    def test_upgrade_show_applied_cmd(self):
        """ Test `upgrade show applied` command. """
        from invenio_upgrader.manage import main
        out = run_py_func(main, 'upgrader show applied').out

        expected = '>>> Following upgrade(s) have been applied:'
        self.assertTrue(expected in out.split('\n'),
                        "%s was not found in output %s" % (expected, out))

    def test_upgrade_show_pending_cmd(self):
        """ Test `upgrade show pending` command. """
        from invenio_upgrader.manage import main
        out = run_py_func(main, 'upgrader show pending').out

        lines = out.split('\n')
        expected = ('>>> Following upgrade(s) are ready to be applied:',
                    '>>> All upgrades have been applied.')
        self.assertTrue(expected[0] in lines or expected[1] in lines,
                        "%s was not found in output %s" % (expected, lines))
