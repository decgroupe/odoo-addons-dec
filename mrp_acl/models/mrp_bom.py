# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import _, models

from . import mrp_production


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def write(self, vals):
        if "code" in vals:
            if (
                self.env.context.get("bypass_supermanager_check")
                or self.user_has_groups(mrp_production.SUPERMANAGER_GROUP)
                or self.env.is_superuser()
            ):
                pass
            else:
                self.env["mrp.production"]._raise_not_supermanager(
                    [_("You are not allowed to edit the code of a BoM")]
                )
        return super().write(vals)
