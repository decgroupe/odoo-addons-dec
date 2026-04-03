# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models


class MrpProductionRequest(models.Model):
    _inherit = "mrp.production.request"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
    )
    zip_id = fields.Many2one(
        related="partner_id.zip_id",
        string="ZIP Location",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Create production requests and auto-populate partner_id from
        sale_order_id."""
        production_requests = super().create(vals_list)
        for production_request in production_requests:
            # use sale_order_id from sale_mrp_production_request_link module
            # to retrieve partner_id
            sale_order_id = production_request.sale_order_id
            if sale_order_id:
                production_request.partner_id = sale_order_id.partner_shipping_id
        return production_requests
