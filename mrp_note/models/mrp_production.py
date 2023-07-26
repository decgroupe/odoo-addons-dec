# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import _, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    note = fields.Text("Internal Notes")

    def write(self, vals):
        if vals.get("note"):
            self.message_post(
                body=_("Internal notes changed to: {}").format(vals.get("note"))
            )
        res = super().write(vals)
        return res
