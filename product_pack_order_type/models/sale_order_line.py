# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pack_order_type = fields.Selection(
        related='product_id.pack_order_type',
    )

    def expand_pack_line(self, write=False):
        self.ensure_one()
        if self.product_id.pack_ok:
            if self.pack_order_type in ('all', 'sale'):
                super().expand_pack_line(write)
