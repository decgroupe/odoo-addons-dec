# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo import _, api, fields, models


class SoftwareLicense(models.Model):
    _inherit = "software.license"

    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Production",
    )

    def _prepare_export_vals(self, include_activation_identifier=True):
        res = super()._prepare_export_vals(include_activation_identifier)
        res["production"] = self.production_id.display_name
        return res
