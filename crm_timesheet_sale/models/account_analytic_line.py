# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    """extend account.analytic.line to link timesheets to sale orders."""

    _inherit = "account.analytic.line"

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
    )
