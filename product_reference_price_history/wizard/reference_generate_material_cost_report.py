# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import api, fields, models


class ReferenceGenerateMaterialCostReport(models.TransientModel):
    _inherit = "wizard.run"
    _name = "reference.generate_material_cost_report"
    _description = "Generate Material Cost Report"

    @api.model
    def _get_default_email_to(self):
        """Return the default recipient email combining system param
        and current user email."""
        return ",".join(
            [
                self.env["ref.reference"]._get_cost_report_default_email(),
                self.env.user.email,
            ]
        )

    use_custom_date_range = fields.Boolean(string="Custom Dates")
    email_to = fields.Char(
        string="To (Emails)",
        help="Comma-separated recipient addresses",
        default=_get_default_email_to,
    )
    format_prices = fields.Boolean(string="Format Prices", default=True)
    date_before = fields.Date(string="Before")
    date_after = fields.Date(string="After")

    def pre_execute(self):
        """Validate that date_after is before date_before when custom dates are used."""
        if self.date_before and self.date_after:
            assert self.date_after < self.date_before

    def execute(self):
        """Execute the report generation with the configured parameters."""
        self.env["ref.reference"].generate_material_cost_report(
            self.date_before,
            self.date_after,
            self.format_prices,
            self.email_to,
        )
