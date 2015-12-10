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

"""Test Invenio Upgrader ordering."""

from __future__ import absolute_import

import pytest

from invenio_upgrader import UpgradeBase


def dictify(ls, value=None):
    """Generate a dict out of a list."""
    if value is not None:
        return {x: value for x in ls}
    else:
        return {x.name: x for x in ls}


def upgrades_str(ls):
    """Generate string containing a list of upgrades."""
    class Xcls(object):
        """Helper to create a string out of a list of upgrades."""

        def __init__(self, id_val):
            self.id = id_val

        def __repr__(self):
            return str(self.id)
    return str([Xcls(x.name) for x in ls])


def create_upgrade(node_id, depends_on, repository):
    """Helper to create upgrade objects."""
    cls = type(
        node_id, (UpgradeBase,),
        {'do_upgrade': lambda: str(node_id),
         'name': node_id,
         'repository': repository}
    )
    cls._depends_on = depends_on
    return cls()


def test_version():
    """Test version import."""
    from invenio_upgrader import __version__
    assert __version__


def test_normal_graph():
    """Normal dependency graph."""
    from invenio_upgrader.engine import InvenioUpgrader
    upgrades = dictify([
        create_upgrade('1', [], 'invenio'),
        create_upgrade('2', ['1'], 'invenio'),
        create_upgrade('3', ['1'], 'invenio'),
        create_upgrade('4', ['2'], 'invenio'),
        create_upgrade('5', ['3', '4'], 'invenio'),
        create_upgrade('6', ['5', ], 'invenio'),
    ])
    m = InvenioUpgrader()
    assert upgrades_str(m.order_upgrades(upgrades)) in [
        "[1, 2, 3, 4, 5, 6]",
        "[1, 2, 4, 3, 5, 6]",
        "[1, 3, 2, 4, 5, 6]",
    ]


def test_two_graphs_graphs():
    """Two independent graphs."""
    from invenio_upgrader.engine import InvenioUpgrader
    upgrades = dictify([
        create_upgrade('1', [], 'invenio'),
        create_upgrade('2', ['1'], 'invenio'),
        create_upgrade('3', ['1'], 'invenio'),

        create_upgrade('a', [], 'other'),
        create_upgrade('b', ['a'], 'other'),
        create_upgrade('c', ['a'], 'other'),

        create_upgrade('4', ['2'], 'invenio'),
        create_upgrade('5', ['3', '4'], 'invenio'),
        create_upgrade('6', ['5', ], 'invenio'),

        create_upgrade('d', ['b'], 'other'),
        create_upgrade('e', ['c', 'd'], 'other'),
        create_upgrade('f', ['e', ], 'other'),
    ])

    m = InvenioUpgrader()
    assert upgrades_str(m.order_upgrades(upgrades)) in [
        "[1, 2, 4, 3, 5, 6, a, b, d, c, e, f]",
        "[1, 2, 4, 3, 5, 6, a, b, c, d, e, f]",
        "[1, 2, 4, 3, 5, 6, a, c, b, d, e, f]",
        "[1, 2, 3, 4, 5, 6, a, b, d, c, e, f]",
        "[1, 2, 3, 4, 5, 6, a, b, c, d, e, f]",
        "[1, 2, 3, 4, 5, 6, a, c, b, d, e, f]",
        "[1, 3, 2, 4, 5, 6, a, b, d, c, e, f]",
        "[1, 3, 2, 4, 5, 6, a, b, c, d, e, f]",
        "[1, 3, 2, 4, 5, 6, a, c, b, d, e, f]",
        "[a, b, d, c, e, f, 1, 2, 4, 3, 5, 6]",
        "[a, b, c, d, e, f, 1, 2, 4, 3, 5, 6]",
        "[a, c, b, d, e, f, 1, 2, 4, 3, 5, 6]",
        "[a, b, d, c, e, f, 1, 2, 3, 4, 5, 6]",
        "[a, b, c, d, e, f, 1, 2, 3, 4, 5, 6]",
        "[a, c, b, d, e, f, 1, 2, 3, 4, 5, 6]",
        "[a, b, d, c, e, f, 1, 3, 2, 4, 5, 6]",
        "[a, b, c, d, e, f, 1, 3, 2, 4, 5, 6]",
        "[a, c, b, d, e, f, 1, 3, 2, 4, 5, 6]",
        ]


def test_cycle_graph():
    """Cycle 2, 4, 3."""
    from invenio_upgrader.engine import InvenioUpgrader
    upgrades = dictify([
        create_upgrade('1', [], 'invenio'),
        create_upgrade('2', ['1', '3'], 'invenio'),
        create_upgrade('3', ['1', '4'], 'invenio'),
        create_upgrade('4', ['2'], 'invenio'),
        create_upgrade('5', ['3', '4'], 'invenio'),
        create_upgrade('6', ['5', ], 'invenio'),
    ])

    m = InvenioUpgrader()
    with pytest.raises(Exception):
        m.order_upgrades(upgrades)


def test_missing_dependency():
    """Missing dependency 0."""
    from invenio_upgrader.engine import InvenioUpgrader
    upgrades = dictify([
        create_upgrade('1', [], 'invenio'),
        create_upgrade('2', ['1'], 'invenio'),
        create_upgrade('3', ['1', '0'], 'invenio'),
    ])

    m = InvenioUpgrader()
    with pytest.raises(Exception):
        m.order_upgrades(upgrades)


def test_cross_graph_dependency():
    """Missing dependency 0."""
    from invenio_upgrader.engine import InvenioUpgrader
    upgrades = dictify([
        create_upgrade('1', [], 'invenio'),
        create_upgrade('2', ['1'], 'invenio'),
        create_upgrade('3', ['1', 'b'], 'invenio'),
        create_upgrade('a', [], 'other'),
        create_upgrade('b', ['a'], 'other'),
        create_upgrade('c', ['2'], 'other'),
    ])

    m = InvenioUpgrader()
    # self.assertRaises(Exception, m.order_upgrades, upgrades)
    assert upgrades_str(m.order_upgrades(upgrades)) in [
        "[1, 2, c, a, b, 3]",
        "[1, 2, a, c, b, 3]",
        "[1, 2, a, b, c, 3]",
        "[1, 2, a, b, 3, c]",
        "[1, a, 2, b, c, 3]",
        "[1, a, 2, b, 3, c]",
        "[1, a, 2, c, b, 3]",
        "[1, a, b, 2, c, 3]",
        "[1, a, b, 2, 3, c]",
        "[1, a, b, 3, 2, c]",
        "[a, 1, 2, c, b, 3]",
        "[a, 1, 2, b, c, 3]",
        "[a, 1, 2, b, 3, c]",
        "[a, 1, b, 3, 2, c]",
        "[a, 1, b, 2, 3, c]",
        "[a, 1, b, 2, c, 3]",
        "[a, b, 1, 3, 2, c]",
        "[a, b, 1, 2, c, 3]",
        "[a, b, 1, 2, 3, c]"
    ]


def test_history():
    """History."""
    from invenio_upgrader.engine import InvenioUpgrader
    upgrades = dictify([
        create_upgrade('1', [], 'invenio'),
        create_upgrade('2', ['1'], 'invenio'),
        create_upgrade('3', ['1'], 'invenio'),
        create_upgrade('4', ['2'], 'invenio'),
        create_upgrade('5', ['3', '4'], 'invenio'),
        create_upgrade('6', ['5', ], 'invenio'),
    ])

    history = dictify(['1', '2', '4'], value=1)
    m = InvenioUpgrader()
    assert upgrades_str(m.order_upgrades(upgrades, history)) == "[3, 5, 6]"

    history = dictify(['3', '5'], value=1)
    m = InvenioUpgrader()
    assert upgrades_str(m.order_upgrades(upgrades, history)) == "[6]"
