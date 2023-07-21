# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_buy(self, procurements):
        alt_procurements = []
        # Ignore orderpoints from `make_to_order` products
        for procurement, rule in procurements:
            if (
                procurement.values.get("orderpoint_id")
                and procurement.product_id.procure_method == "make_to_order"
            ):
                _logger.info(
                    _(
                        "Ignore stock.rule for `make_to_order` product {}, "
                        "please consider to archive or delete its orderpoints"
                    ).format(
                        procurement.product_id.display_name,
                    )
                )
            else:
                alt_procurements.append((procurement, rule))
        return super()._run_buy(alt_procurements)
