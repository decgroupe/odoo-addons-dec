# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023


from odoo import api, fields, models


class SoftwareLicenseHardware(models.Model):
    _inherit = "software.license.hardware"

    pass_id = fields.Many2one(
        comodel_name="software.license.pass",
        related="license_id.pass_id",
        store=True,
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.license_id.pass_id:
            record.license_id.pass_id._check_max_allowed_hardware()
        return record

    def write(self, vals):
        res = super().write(vals)
        # the code below is a security added to ensure a consistent pass state but
        # it will probably be never reached because an exception will be raised
        # in the parent write for the same reason
        pass_ids = self.mapped("license_id").mapped("pass_id")
        if pass_ids and not self.env.context.get("bypass_pass_checks", False):
            pass_ids._check_max_allowed_hardware()
        return res
