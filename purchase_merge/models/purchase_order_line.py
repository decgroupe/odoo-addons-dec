# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2026

import logging

from odoo import models

_logger = logging.getLogger(__name__)

try:
    from prettytable import PrettyTable
except ImportError:
    _logger.warning(
        "prettytable module not found, "
        "please install it to get better logging of order line recomputation"
    )
    PrettyTable = None


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _compute_price_unit_and_date_planned_and_name(self):
        """Wrap original method to log recomputation of order lines."""
        # capture pre-values for each line
        pre_values = {}
        for line in self:
            pre_values[line.id] = {
                "price_unit": line.price_unit,
                "name": line.name,
                "date_planned": line.date_planned,
            }

        super()._compute_price_unit_and_date_planned_and_name()
        # log a small diff table per line showing before -> after
        for line in self:
            before = pre_values.get(line.id, {})
            after = {
                "price_unit": line.price_unit,
                "name": line.name,
                "date_planned": line.date_planned,
            }
            if PrettyTable:
                table = PrettyTable()
                table.align = "l"
                table.field_names = ["field", "before", "after"]
                for field in ["price_unit", "name", "date_planned"]:
                    table.add_row([field, before.get(field), after.get(field)])
                _logger.info("Diff for line %s:\n%s", line.id, table)
            else:
                _logger.info(
                    "Diff for line %s:\nBefore: %s\nAfter: %s", line.id, before, after
                )
