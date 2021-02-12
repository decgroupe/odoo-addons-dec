# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import api, models


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    @api.multi
    def _prepare_manufacturing_order(self):
        vals = super()._prepare_manufacturing_order()
        request_id = self.mrp_production_request_id
        vals['partner_id'] = request_id.partner_id.id
        return vals
