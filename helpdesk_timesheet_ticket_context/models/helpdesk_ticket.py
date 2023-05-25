# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import api, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def create(self, vals):
        if "name" not in vals:
            vals["name"] = vals.pop("number", "...")
        res = super().create(vals)
        return res
