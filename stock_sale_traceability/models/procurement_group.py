# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo import models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    def get_head_desc(self):
        """Override to use the sale order name as description when linked to a sale."""
        head, desc = super().get_head_desc()
        g = self.sudo()
        if g.sale_id and g.sale_id.name != g.name:
            desc = g.sale_id.name
        return head, desc
