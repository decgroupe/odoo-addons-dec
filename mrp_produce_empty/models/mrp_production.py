# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Aug 2020

from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    @api.depends('move_raw_ids.state', 'workorder_ids.move_raw_ids', 'bom_id.ready_to_produce')
    def _compute_availability(self):
        super()._compute_availability()
        for order in self:
            if not order.move_raw_ids:
                # Override availability from 'none' (min) to 'assigned' (max)
                # This will allow us to display the 'Produce' button
                order.availability = 'assigned'
                continue
