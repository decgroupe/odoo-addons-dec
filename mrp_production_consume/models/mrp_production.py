# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def post_inventory(self):
        res = super().post_inventory()
        self.update_unit_factor()
        return res

    def update_unit_factor(self):
        for production in self:
            production_qty = (production.product_qty - production.qty_produced) or 1.0
            for move in production.move_raw_ids:
                move.unit_factor = move.product_uom_qty / production_qty

    def open_consume(self):
        self.ensure_one()
        action = self.env.ref("mrp_production_consume.act_mrp_consume").read()[0]
        return action
