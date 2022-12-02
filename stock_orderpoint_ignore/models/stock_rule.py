# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import logging
from odoo import api, models, _

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _run_buy(self, product_id, product_qty, product_uom, location_id, \
        name, origin, values):
        # Ignore orderpoints from `make_to_order` products
        if values.get('orderpoint_id') and product_id.procure_method == 'make_to_order':
            _logger.info(
                _(
                    "Ignore stock.rule for `make_to_order` product {}, "
                    "please consider to archive or delete its orderpoints"
                ).format(product_id.display_name, )
            )
        else:
            super()._run_buy(
                product_id,
                product_qty,
                product_uom,
                location_id,
                name,
                origin,
                values,
            )
