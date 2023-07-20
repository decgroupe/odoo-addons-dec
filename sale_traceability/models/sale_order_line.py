# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2023

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_head_desc(self):
        state = dict(self._fields["state"]._description_selection(self.env)).get(
            self.state
        )
        head = "📈{0}".format(self.order_id.name)
        desc = "{0}{1}".format(self.order_id.state_emoji, state)
        return head, desc
