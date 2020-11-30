# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import logging

from odoo import _, api, fields, models

from odoo.addons.tools_miscellaneous.tools.html_helper import (
    format_hd,
    div,
)

_logger = logging.getLogger(__name__)


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def get_head_desc(self):
        head = '🧮{0}'.format(self.name)
        # WARNING: the string character is a non-breaking space
        desc = '{} ≤ 𝜕 ≤ {} ↗ ×{}'.format(
            self.product_min_qty,
            self.product_max_qty,
            self.qty_multiple,
        )
        return head, desc
