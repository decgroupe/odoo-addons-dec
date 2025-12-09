# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    # addons/mrp/models/mrp_production.py
    mrp_production_ids = fields.One2many(
        comodel_name="mrp.production",
        inverse_name="procurement_group_id",
    )
    mrp_production_count = fields.Integer(
        compute="_compute_mrp_production_order",
        string="Production count",
        default=0,
        store=False,
    )

    def _compute_mrp_production_order(self):
        for procurement in self:
            procurement.mrp_production_count = len(procurement.mrp_production_ids)

    def action_view_mrp_productions(self):
        self.ensure_one()
        action = self.env["mrp.production"].action_view()
        action["domain"] = [("procurement_group_id", "=", self.id)]
        action["context"] = {}
        return action
