# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014, 2015 CERN.
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


"""Click command-line interface for upgrader management."""

from __future__ import absolute_import, print_function

import click
import os

from datetime import date
from flask import current_app
from flask_cli import with_appcontext
from werkzeug.utils import import_string

from .engine import InvenioUpgrader
from .operations import produce_upgrade_operations


UPGRADE_TEMPLATE = """# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) %(year)s CERN.
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

import warnings

from invenio_db import db
from invenio_upgrader import op, UpgradeBase

from sqlalchemy import *

%(imports)s

class %(cls)s(UpgradeBase):
    \"\"\"Upgrade description here.\"\"\"

    # Important: Below is only a best guess. You MUST validate which previous
    # upgrade you depend on.
    _depends_on = %(depends_on)s

    def do_upgrade(self):
        \"\"\"Implement your upgrades here.\"\"\"
    %(operations)s

    def estimate(self):
        \"\"\"Estimate running time of upgrade in seconds (optional).\"\"\"
        return 1

    def pre_upgrade(self):
        \"\"\"Run pre-upgrade checks (optional).\"\"\"
        # Example of raising errors:
        # raise RuntimeError("Description of error 1")

    def post_upgrade(self):
        \"\"\"Run post-upgrade checks (optional).\"\"\"
        # Example of issuing warnings:
        # warnings.warn("A continuable error occurred")
"""


@click.group()
def upgrader():
    """Upgrader management commands."""


@upgrader.command()
@with_appcontext
def run():
    """Command for applying upgrades."""
    logfilename = os.path.join(current_app.config['CFG_LOGDIR'],
                               'invenio_upgrader.log')
    upgrader = InvenioUpgrader()
    logger = upgrader.get_logger(logfilename=logfilename)

    try:
        upgrades = upgrader.get_upgrades()

        if not upgrades:
            logger.info("All upgrades have been applied.")
            return

        logger.info("Following upgrade(s) will be applied:")

        for u in upgrades:
            logger.info(" * %s (%s)" % (u.name, u.info))

        logger.info("Running pre-upgrade checks...")
        upgrader.pre_upgrade_checks(upgrades)

        logger.info("Calculating estimated upgrade time...")
        estimate = upgrader.human_estimate(upgrades)

        click.confirm(
            "You are going to upgrade your installation "
            "(estimated time: {0})!".format(estimate), abort=True)

        for u in upgrades:
            logger.info("Applying %s (%s)" % (u.name, u.info))
            upgrader.apply_upgrade(u)

        logger.info("Running post-upgrade checks...")
        upgrader.post_upgrade_checks(upgrades)

        if upgrader.has_warnings():
            logger.warning("Upgrade completed with %s warnings - please check "
                           "log-file for further information:\nless %s"
                           % (upgrader.get_warnings_count(), logfilename))
        else:
            logger.info("Upgrade completed successfully.")
    except RuntimeError as e:
        for msg in e.args:
            logger.error(unicode(msg))
        logger.info("Please check log file for further information:\n"
                    "less %s" % logfilename)
        click.Abort()


@upgrader.command()
@with_appcontext
def check():
    """Command for checking upgrades."""
    upgrader = InvenioUpgrader()
    logger = upgrader.get_logger()

    try:
        # Run upgrade pre-checks
        upgrades = upgrader.get_upgrades()

        # Check if there's anything to upgrade
        if not upgrades:
            logger.info("All upgrades have been applied.")
            return

        logger.info("Following upgrade(s) have not been applied yet:")
        for u in upgrades:
            logger.info(
                " * {0} {1}".format(u.name, u.info))

        logger.info("Running pre-upgrade checks...")
        upgrader.pre_upgrade_checks(upgrades)
        logger.info("Upgrade check successful - estimated time for upgrading"
                    " Invenio is %s..." % upgrader.human_estimate(upgrades))
    except RuntimeError as e:
        for msg in e.args:
            logger.error(unicode(msg))
        logger.error("Upgrade check failed. Aborting.")
        raise


@upgrader.command()
@with_appcontext
def pending():
    """Command for showing upgrades ready to be applied."""
    upgrader = InvenioUpgrader()
    logger = upgrader.get_logger()

    try:
        upgrades = upgrader.get_upgrades()

        if not upgrades:
            logger.info("All upgrades have been applied.")
            return

        logger.info("Following upgrade(s) are ready to be applied:")

        for u in upgrades:
            logger.info(
                " * {0} {1}".format(u.name, u.info))
    except RuntimeError as e:
        for msg in e.args:
            logger.error(unicode(msg))
        raise


@upgrader.command()
@with_appcontext
def applied():
    """Command for showing all upgrades already applied."""
    upgrader = InvenioUpgrader()
    logger = upgrader.get_logger()

    try:
        upgrades = upgrader.get_history()

        if not upgrades:
            logger.info("No upgrades have been applied.")
            return

        logger.info("Following upgrade(s) have been applied:")

        for u_id, applied in upgrades:
            logger.info(" * %s (%s)" % (u_id, applied))
    except RuntimeError as e:
        for msg in e.args:
            logger.error(unicode(msg))
        raise


@upgrader.command()
@click.option('-p', '--path')
@click.option('-r', '--repository', default='invenio')
@with_appcontext
def release(path, repository):
    """Create a new release upgrade recipe, for developers."""
    upgrader = InvenioUpgrader()
    logger = upgrader.get_logger()

    try:
        endpoints = upgrader.find_endpoints()

        if not endpoints:
            logger.error("No upgrades found.")
            click.Abort()

        depends_on = []
        for repo, upgrades in endpoints.items():
            depends_on.extend(upgrades)

        return recipe(path,
                      repository=repository,
                      depends_on=depends_on,
                      release=True,
                      output_path=output_path)

    except RuntimeError as e:
        for msg in e.args:
            logger.error(unicode(msg))
        raise


@upgrader.command()
@click.option('-p', '--package', required=True,
              help="Import path of module where to create recipe (required).")
@click.option('-o', '--path', 'output_path', help="Override output path.")
@click.option('-r', '--repository', help="Override repository name")
@click.option('-n', '--name', help="Name of upgrade file")
@click.option('-d', '--depends_on', help="List of recipes to depend on.")
@click.option('-a', '--auto', is_flag=True, default=False,
              help="Auto-generate upgrade (default: False).")
@click.option('--release', is_flag=True, default=False)
@click.option('--overwrite', is_flag=True, default=False)
@with_appcontext
def recipe(package, repository=None, depends_on=None, release=False,
           output_path=None, auto=False, overwrite=False, name=None):
    """Create a new upgrade recipe, for developers."""
    upgrader = InvenioUpgrader()
    logger = upgrader.get_logger()

    try:
        path, found_repository = _upgrade_recipe_find_path(package)

        if output_path:
            path = output_path

        if not repository:
            repository = found_repository

        if not os.path.exists(path):
            raise RuntimeError("Path does not exists: %s" % path)
        if not os.path.isdir(path):
            raise RuntimeError("Path is not a directory: %s" % path)

        # Generate upgrade filename
        if release:
            filename = "%s_release_x_y_z.py" % repository
        else:
            filename = "%s_%s_%s.py" % (repository,
                                        date.today().strftime("%Y_%m_%d"),
                                        name or 'rename_me')

        # Check if generated repository name can be parsed
        test_repository = upgrader._parse_plugin_id(filename[:-3])
        if repository != test_repository:
            raise RuntimeError(
                "Generated repository name cannot be parsed. "
                "Please override it with --repository option."
            )

        upgrade_file = os.path.join(path, filename)

        if os.path.exists(upgrade_file) and not overwrite:
                raise RuntimeError(
                    "Could not generate upgrade - %s already exists."
                    % upgrade_file
                )

        # Determine latest installed upgrade
        if depends_on is None:
            depends_on = ["CHANGE_ME"]

            u = upgrader.latest_applied_upgrade(repository=repository)
            if u:
                depends_on = [u]

        # Write upgrade template file
        _write_template(
            upgrade_file, name or 'rename_me',
            depends_on, repository, auto=auto)

        logger.info("Created new upgrade %s" % upgrade_file)
    except RuntimeError as e:
        for msg in e.args:
            logger.error(unicode(msg))
        raise


#
# Helper functions
#
def _write_template(upgrade_file, name, depends_on, repository, auto=False):
    """Write template to upgrade file."""
    if auto:
        # Ensure all models are loaded
        from invenio_db import models
        list(models)
        template_args = produce_upgrade_operations()
        operations_str = template_args['upgrades']
        import_str = template_args['imports']
    else:
        operations_str = "    pass"
        import_str = ""

    with open(upgrade_file, 'w') as f:
        f.write(UPGRADE_TEMPLATE % {
            'depends_on': depends_on,
            'repository': repository,
            'year': date.today().year,
            'operations': operations_str,
            'imports': import_str,
            'cls': ''.join(w.capitalize() or '_' for w in name.split('_'))
        })


def _upgrade_recipe_find_path(import_str, create=True):
    """Determine repository name and path for new upgrade.

    It is based on package import path.
    """
    try:
        # Import package
        m = import_string(import_str)

        # Check if package or module
        if m.__package__ is not None and m.__package__ != m.__name__:
            raise RuntimeError(
                "Expected package but found module at '%s'." % import_str
            )

        # Create upgrade directory if it does not exists
        path = os.path.join(os.path.dirname(m.__file__), "upgrades")
        if not os.path.exists(path) and create:
            os.makedirs(path)

        # Create init file if it does not exists
        init = os.path.join(path, "__init__.py")
        if not os.path.exists(init) and create:
            open(init, 'a').close()

        repository = m.__name__.split(".")[-1]

        return (path, repository)
    except ImportError:
        raise RuntimeError("Could not find module '%s'." % import_str)
    except SyntaxError:
        raise RuntimeError("Module '%s' has syntax errors." % import_str)
