# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import models


class UoM(models.Model):
    _inherit = "uom.uom"

    def _check_category_reference_uniqueness(self):
        """Override to skip category validation when the context flag is set."""
        if self.env.context.get("skip_uom_category_validation"):
            return
        return super()._check_category_reference_uniqueness()
