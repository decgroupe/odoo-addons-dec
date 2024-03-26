# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_generate_signatures(self):
        global_template = self.env.ref("res_users_signature.user_signature_template")
        for user in self:
            template = user.signature_template or global_template
            user._generate_from_template(template)
