# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super().product_id_change()
        if self.product_id and self.product_id.public_code:
            parts = list(self.name.partition('\n'))
            parts[0] = '[{}] {}'.format(
                self.product_id.public_code, self.product_id.name
            )
            self.name = ''.join(parts)
        return res
