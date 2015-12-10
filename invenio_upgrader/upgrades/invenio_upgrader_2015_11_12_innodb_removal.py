# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

"""Remove InnoDB upgrade recipe."""

import warnings

from invenio_db import db
from sqlalchemy.sql import text

from invenio_upgrader import UpgradeBase, op


class InnoDBRemoval(UpgradeBase):
    """Remove InnoDB upgrade recipe."""

    _depends_on = []

    def do_upgrade(self):
        """Implement your upgrades here."""
        sql = text('delete from upgrade where upgrade = :upgrade')
        db.engine.execute(
            sct(ql, upgrade='invenio_upgrader_2015_11_12_innodb_removal'))

    def pre_upgrade(self):
        """Run pre-upgrade checks (optional)."""
        sql = text('select 1 from upgrade where upgrade = :upgrade')
        if not db.engine.execute(
            sql, upgrade='invenio_upgrader_2015_11_12_innodb_removal'
           ).fetchall():
            warnings.warn("Upgrade '{}' was not applied.".format(
                'invenio_upgrader_2015_11_12_innodb_removal'))
