# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_shipping_zip_id = fields.Many2one(
        comodel_name="res.city.zip",
        related="partner_shipping_id.zip_id",
        string="Shipping Partner's ZIP",
        readonly=True,
        store=True,
    )
    partner_shipping_country_id = fields.Many2one(
        comodel_name="res.country",
        related="partner_shipping_id.country_id",
        string="Shipping Partner's Country",
        store=True,
    )
