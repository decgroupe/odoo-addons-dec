# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def delegate_create_contact(self, vals):
        vals["inherit_commercial_partner"] = False
        return super().delegate_create_contact(vals)
