# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def print_quotation(self):
        for order in self:
            if order.user_id == self.env.ref('base.user_root'):
                order.user_id = self.env.user
        return super().print_quotation()
