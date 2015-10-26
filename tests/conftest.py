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

"""Pytest configuration."""

import os
import pytest
import shutil
import sys
import tempfile

from flask import Flask


@pytest.fixture()
def tmpdir(request):
    """Setup a test python package, to test upgrade recipe creation."""
    tmpdir = tempfile.mkdtemp()
    pkg_path = os.path.join(tmpdir, 'invenio_upgrader_test')
    os.makedirs(pkg_path)
    open(os.path.join(pkg_path, '__init__.py'), 'a').close()
    pkg_path_mymod = os.path.join(
        tmpdir, 'invenio_upgrader_test', 'mymod'
    )
    os.makedirs(pkg_path_mymod)

    open(os.path.join(pkg_path, '__init__.py'), 'a').close()
    open(os.path.join(pkg_path_mymod, '__init__.py'), 'a').close()

    sys.path.append(tmpdir)
    import invenio_upgrader_test
    import invenio_upgrader_test.mymod

    def clean():
        """Remove test package again."""
        sys.path.remove(tmpdir)
        keys = []
        for m in sys.modules:
            if m.startswith('invenio_upgrader_test'):
                keys.append(m)
        for k in keys:
            del sys.modules[k]

        try:
            import invenio_upgrader_test
            raise AssertionError("Test package not removed from sys.path")
        except ImportError:
            pass

        shutil.rmtree(tmpdir)

    request.addfinalizer(clean)
    return tmpdir


@pytest.fixture()
def app():
    """Flask application fixture."""
    app = Flask('testapp')
    app.config.update(
        SECRET_KEY="CHANGE_ME",
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'
        ),
        CFG_LOGDIR='/tmp',
        TESTING=True,
    )
    return app
