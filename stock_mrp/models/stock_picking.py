# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, July 2020

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    production_ids = fields.Many2many(
        comodel_name="mrp.production",
        compute="_compute_production_ids",
        string="Manufacturing orders associated to this picking",
    )
    production_count = fields.Integer(
        compute="_compute_production_ids",
        string="Number of Manufacturing Orders",
    )

    @api.depends("group_id")
    def _compute_production_ids(self):
        for picking in self:
            picking.production_ids = self.env["mrp.production"].search(
                [
                    ("procurement_group_id", "=", picking.group_id.id),
                    ("procurement_group_id", "!=", False),
                ]
            )
            picking.production_count = len(picking.production_ids)
