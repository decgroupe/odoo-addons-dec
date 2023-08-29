# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa@decgroupe.com>, Aug 2023

from odoo import _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        res = super().write(vals)
        if self and vals.get("product_uom_qty"):
            if self.production_id and self.product_uom_qty <= 0:
                raise UserError(
                    _("You cannot produce a zero quantity for %s") % (self,)
                )
        return res
