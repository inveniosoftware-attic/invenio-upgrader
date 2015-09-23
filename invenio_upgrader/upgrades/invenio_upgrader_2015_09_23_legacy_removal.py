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

"""Remove legacy upgrade recipes."""

import warnings

from invenio_ext.sqlalchemy import db
from invenio_upgrader.api import op

from sqlalchemy.sql import text

depends_on = []

legacy_upgrades = [
    'invenio_2012_10_29_idxINDEX_new_indexer_column',
    'invenio_2012_10_31_WebAuthorProfile_bibformat_dependency_update',
    'invenio_2012_10_31_tablesorter_location',
    'invenio_2012_11_01_lower_user_email',
    'invenio_2012_11_04_circulation_and_linkback_updates',
    'invenio_2012_11_07_xtrjob_last_recid',
    'invenio_2012_11_15_bibdocfile_model',
    'invenio_2012_11_15_hstRECORD_marcxml_longblob',
    'invenio_2012_11_21_aiduserinputlog_userid_check',
    'invenio_2012_11_27_new_selfcite_tables',
    'invenio_2012_12_05_oaiHARVEST_arguments_blob',
    'invenio_2012_12_06_new_citation_dict_table',
    'invenio_2012_12_11_new_citation_errors_table',
    'invenio_2013_01_08_new_goto_table',
    'invenio_2013_01_12_bibrec_master_format',
    'invenio_2013_02_01_oaiREPOSITORY_last_updated',
    'invenio_2013_02_06_new_collectionboxname_table',
    'invenio_2013_03_07_crcILLREQUEST_overdue_letter',
    'invenio_2013_03_18_aidPERSONIDDATA_last_updated',
    'invenio_2013_03_18_bibauthorid_search_engine_tables',
    'invenio_2013_03_18_wapCACHE_object_value_longblob',
    'invenio_2013_03_20_idxINDEX_synonym_kb',
    'invenio_2013_03_20_new_self_citation_dict_table',
    'invenio_2013_03_21_idxINDEX_stopwords',
    'invenio_2013_03_25_idxINDEX_html_markup',
    'invenio_2013_03_26_new_citation_log_table',
    'invenio_2013_03_28_bibindex_bibrank_type_index',
    'invenio_2013_03_28_idxINDEX_tokenizer',
    'invenio_2013_03_29_idxINDEX_stopwords_update',
    'invenio_2013_04_11_bibformat_2nd_pass',
    'invenio_2013_04_30_new_plotextractor_websubmit_function',
    'invenio_2013_06_11_rnkDOWNLOADS_file_format',
    'invenio_2013_06_20_new_bibcheck_rules_table',
    'invenio_2013_06_24_new_bibsched_status_table',
    'invenio_2013_08_20_bibauthority_updates',
    'invenio_2013_08_22_hstRECORD_affected_fields',
    'invenio_2013_08_22_new_index_itemcount',
    'invenio_2013_09_02_new_bibARXIVPDF',
    'invenio_2013_09_10_new_param_websubmit_function',
    'invenio_2013_09_13_new_bibEDITCACHE',
    'invenio_2013_09_16_aidPERSONIDDATA_datablob',
    'invenio_2013_09_25_virtual_indexes',
    'invenio_2013_09_26_webauthorlist',
    'invenio_2013_09_30_indexer_interface',
    'invenio_2013_10_11_bibHOLDINGPEN_longblob',
    'invenio_2013_10_18_crcLIBRARY_type',
    'invenio_2013_10_18_new_index_filetype',
    'invenio_2013_10_25_delete_recjson_cache',
    'invenio_2013_10_25_new_param_websubmit_function',
    'invenio_2013_11_12_new_param_websubmit_function',
    'invenio_2013_12_04_seqSTORE_larger_value',
    'invenio_2013_12_05_new_index_doi',
    'invenio_2014_01_22_queue_table_virtual_index',
    'invenio_2014_01_22_redis_sessions',
    'invenio_2014_01_24_seqSTORE_larger_value',
    'invenio_2014_03_13_new_index_filename',
    'invenio_2014_06_02_oaiHARVEST_arguments_cfg_namechange',
    'invenio_2014_08_12_format_code_varchar20',
    'invenio_2014_08_13_tag_recjsonvalue',
    'invenio_2014_08_31_next_collection_tree',
    'invenio_2014_09_09_tag_recjsonvalue_not_null',
    'invenio_2014_11_04_format_recjson',
    'invenio_2015_01_13_hide_holdings',
    'invenio_2015_03_03_tag_value',
    'invenio_2015_04_15_collection_names_with_slashes',
    'invenio_release_1_1_0',
    'invenio_release_1_2_0',
    'submit_2015_03_03_fix_models',
    'submit_2015_04_30_fix_models_sbmFORMATEXTENSION_sbmGFILERESULT',
]

def info():
    """Info message."""
    return __doc__


def do_upgrade():
    """Implement your upgrades here."""
    sql = text('delete from upgrade where upgrade = :upgrade')
    for upgrade in legacy_upgrades:
        db.engine.execute(sql, upgrade=upgrade)


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    sql = text('select 1 from upgrade where upgrade = :upgrade')
    for upgrade in legacy_upgrades:
        if not db.engine.execute(sql, upgrade=upgrade).fetchall():
            warnings.warn("Upgrade '{}' was not applied.".format(upgrade))


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    # Example of issuing warnings:
    # warnings.warn("A continuable error occurred")
