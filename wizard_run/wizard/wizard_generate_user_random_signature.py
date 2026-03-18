# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import models


class WizardGenerateUserRandomSignature(models.TransientModel):
    _inherit = "wizard.run"
    _name = "wizard.generate_user_random_signature"
    _description = "Generate Random Signature for Users"

    def pre_execute(self):
        pass

    def execute(self):
        user_ids = self.env["res.users"].search([])
        user_ids.generate_random_signature()
