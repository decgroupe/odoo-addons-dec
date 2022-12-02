# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_sellers(self, params):
        """
        Sort by minimum quantity in reverse order to select the right
        supplier. The sequence is still used to filter multiple
        possibilities with same quantities
        """
        seller_ids = super()._prepare_sellers(params)
        return seller_ids.sorted(
            key=lambda r: (r.min_qty, 1.0 / (r.sequence or 1.0)), reverse=True
        )
