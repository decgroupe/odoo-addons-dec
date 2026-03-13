# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import models


class Production(models.Model):
    _inherit = "mrp.production"

    def get_head_state_code_symbol(self):
        state, code, symbol = super().get_head_state_code_symbol()
        if self.stage_id:
            state = self.stage_id.name
            code = self.stage_id.code
            symbol = self.stage_id.symbol
        return state, code, symbol
