# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def write(self, values):
        if 'group_id' in values:
            lines = self.env['purchase.order.line']
            for order in self:
                lines += order.order_line.filtered(
                    lambda line: not line.procurement_group_id
                )
            if lines:
                lines.write({
                    'procurement_group_id': values['group_id']
                })
        return super().write(values)
