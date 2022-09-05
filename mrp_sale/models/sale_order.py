# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_view_production(self):
        """ Override `action_view_production` from `sale_mrp_link` to use the
            kanban view from `mrp_stage`
        """
        action = self.production_ids.action_view_staged()
        action["context"] = {}
        return action
