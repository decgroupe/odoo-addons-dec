# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    qty_multiple = fields.Float(
        compute="_compute_qty_multiple",
        help="This value is automatically computed from the product purchase UoM",
        required=False,
    )

    @api.multi
    @api.depends('product_id.uom_po_id')
    def _compute_qty_multiple(self):
        for op in self:
            op.qty_multiple = op.product_id.uom_po_id.factor_inv
