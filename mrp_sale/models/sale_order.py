# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # production order link counter-parts implementation from `sale_mrp_link`
    # these will be combined to existing `mrp_production_ids` from `sale_mrp`
    production_ids = fields.One2many(
        comodel_name="mrp.production",
        inverse_name="sale_order_id",
    )

    @api.depends("production_ids")
    def _compute_mrp_production_ids(self):
        res = super()._compute_mrp_production_ids()
        for sale in self:
            sale.mrp_production_ids = sale.mrp_production_ids | sale.production_ids
            sale.mrp_production_count = len(sale.mrp_production_ids)
        return res

    def action_view_mrp_production(self):
        """Override `action_view_mrp_production` from `sale_mrp` to use the
        kanban view from `mrp_stage`
        """
        action = self.mrp_production_ids.action_view_staged()
        action["context"] = {}
        return action
