# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2023

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_head_desc(self):
        return self.order_id.get_head_desc()
