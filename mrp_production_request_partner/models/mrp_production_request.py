# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import models, api, fields


class MrpProductionRequest(models.Model):
    _inherit = 'mrp.production.request'

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
    )
    zip_id = fields.Many2one(
        related='partner_id.zip_id',
        string='ZIP Location',
    )

    @api.model
    def create(self, values):
        production_request = super().create(values)
        # Use sale_order_id from sale_mrp_production_request_link module
        # to retrieve partner_id
        sale_order_id = production_request.sale_order_id
        if sale_order_id:
            production_request.partner_id = sale_order_id.partner_shipping_id
        return production_request
