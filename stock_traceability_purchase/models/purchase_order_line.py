# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def get_head_desc(self):
        state = dict(self._fields["state"]._description_selection(self.env)).get(
            self.state
        )
        head = f"🛒{self.order_id.name}"
        desc = f"{self.order_id.state_symbol}{state}"
        return head, desc

    def write(self, vals):
        if "move_dest_ids" in vals:
            for move in self.move_dest_ids:
                move._archive_created_purchase_lines()
        return super().write(vals)
