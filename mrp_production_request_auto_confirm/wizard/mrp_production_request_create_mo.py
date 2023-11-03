# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo import models


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    def create_mo(self):
        self.ensure_one()
        action = super().create_mo()
        production_id = self.env["mrp.production"].browse(action["res_id"])
        production_id.action_confirm()
        return action
