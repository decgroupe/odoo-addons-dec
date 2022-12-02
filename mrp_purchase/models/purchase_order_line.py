# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    production_id = fields.Many2one(
        'mrp.production',
        string="Production Order",
        compute='_compute_production_id',
    )
    production_ids = fields.Many2many(
        'mrp.production',
        'purchase_order_line_mrp_rel',
        'purchase_line_id',
        'production_id',
        string="Production Orders",
        readonly=True,
        copy=False,
        help="Production order that created this line",
    )
    bom_line_id = fields.Many2one(
        'mrp.bom.line',
        string="Line of the Bill of Material",
    )

    @api.depends('production_ids')
    def _compute_production_id(self):
        for p in self:
            p.production_id = p.production_ids[:1].id
