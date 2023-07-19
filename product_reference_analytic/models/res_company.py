# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    auto_create_reference_category_analytic_account = fields.Boolean(
        default=True,
    )
