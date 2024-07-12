# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024


from odoo import fields, models


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the maintenance request without "
        "deleting it.",
    )

    def write(self, vals):
        if "archive" in vals:
            vals["active"] = not vals["archive"]
        elif "active" in vals:
            vals["archive"] = not vals["active"]
        active = vals.get("active")
        res = super().write(vals)
        return res
