# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_split(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase_split.action_purchase_order_line_tree"
        )
        return action
