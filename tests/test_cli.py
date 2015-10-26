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

from __future__ import absolute_import, print_function

import os
import pytest
import six
import importlib
from datetime import date

from click.testing import CliRunner
from flask import Flask
from flask_cli import FlaskCLI, ScriptInfo
from invenio_db import InvenioDB, db
from invenio_db.cli import db as db_cmd
from sqlalchemy_utils.functions import create_database, drop_database

from invenio_upgrader import InvenioUpgrader, cli, UpgradeBase


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    FlaskCLI(app)
    ext = InvenioUpgrader(app)
    assert 'invenio-upgrader' in app.extensions

    app = Flask('testapp')
    FlaskCLI(app)
    ext = InvenioUpgrader()
    assert 'invenio-upgrader' not in app.extensions
    ext.init_app(app)
    assert 'invenio-upgrader' in app.extensions


def test_cli(app, tmpdir, monkeypatch):
    """Test CLI."""
    FlaskCLI(app)
    InvenioDB(app)
    InvenioUpgrader(app)

    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)

    assert len(db.metadata.tables) == 1

    runner.invoke(db_cmd, ['init'], obj=script_info)
    runner.invoke(db_cmd, ['create'], obj=script_info)

    result = runner.invoke(cli.applied, obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(cli.pending, obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(cli.check, obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(
        cli.recipe,
        ['-p', 'invenio_upgrader_test.mymod',
         '-d', ['test1', 'test2'],
         '-n','test_name'],
        obj=script_info)
    assert result.exit_code == 0
    expexted_name = "mymod_{0}_test_name".format(
        date.today().strftime("%Y_%m_%d"))
    mod = importlib.import_module(
        'invenio_upgrader_test.mymod.upgrades.{0}'.format(
        expexted_name))
    upgrade = mod.TestName()
    # Test API of created upgrade recipe
    assert upgrade.depends_on == ['test1', 'test2']
    assert upgrade.estimate() == 1
    assert isinstance(upgrade.info, six.string_types)
    upgrade.pre_upgrade()
    upgrade.do_upgrade()
    upgrade.post_upgrade()

    class TestUpgrade(UpgradeBase):
        """Test Upgrade."""
        def do_upgrade(self):
            """Do upgrade."""
            pass

    monkeypatch.setattr(
        'invenio_upgrader.engine.InvenioUpgrader._load_upgrades',
        lambda self, remove_applied: {'test_cli:TestUpgrade': TestUpgrade()})
    result = runner.invoke(cli.run, input='y', obj=script_info)
    assert result.exit_code == 0
    assert '* test_cli:TestUpgrade (Test Upgrade.)' in result.output

    runner.invoke(db_cmd, ['drop', '--yes-i-know'], obj=script_info)
    runner.invoke(db_cmd, ['destroy', '--yes-i-know'], obj=script_info)
