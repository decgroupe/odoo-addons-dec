# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    partner_zip_id = fields.Many2one(
        comodel_name="res.city.zip",
        related="partner_id.zip_id",
        string="Partner's ZIP",
        store=True,
    )
    partner_city_id = fields.Many2one(
        comodel_name="res.city",
        related="partner_id.city_id",
        string="Partner's City",
        store=True,
    )
