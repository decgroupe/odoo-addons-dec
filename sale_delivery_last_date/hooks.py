# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)

try:
    from openupgradelib import openupgrade
except (ImportError, IOError) as err:
    _logger.debug(err)


def rename_module(cr):
    openupgrade.update_module_names(
        cr,
        [("sale_delivery_date", "sale_delivery_last_date")],
        merge_modules=True,
    )
