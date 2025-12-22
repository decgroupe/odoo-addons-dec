# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models


class MrpProductionRequest(models.Model):
    _name = "mrp.production.request"
    _inherit = ["mrp.production.request", "mail.activity.mixin"]

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Source Sale Order",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # same logic than sale_mrp_link
        for vals in vals_list:
            if "origin" in vals:
                # checking first if this comes from a 'sale.order'
                sale_id = self.env["sale.order"].search(
                    [("name", "=", vals["origin"])], limit=1
                )
                if sale_id:
                    vals["sale_order_id"] = sale_id.id
                    if sale_id.client_order_ref:
                        vals["origin"] = sale_id.client_order_ref
                else:
                    # checking if this production request comes from a route
                    production_id = self.env["mrp.production"].search(
                        [("name", "=", vals["origin"])]
                    )
                    # if so, use the 'sale_order_id' from the parent production
                    vals["sale_order_id"] = production_id.sale_order_id.id
        record_ids = super().create(vals_list)
        return record_ids

    def button_approved(self):
        self.write({"assigned_to": self.env.uid})
        return super().button_approved()
