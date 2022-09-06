# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_open_as_product(self):
        action = self.mapped('product_tmpl_id').action_view()
        action['context'] = {}
        return action
