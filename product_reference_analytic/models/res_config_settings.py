# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_create_reference_category_analytic_account = fields.Boolean(
        related="company_id.auto_create_reference_category_analytic_account",
        readonly=False,
    )
