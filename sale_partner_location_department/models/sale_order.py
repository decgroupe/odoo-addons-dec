# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_shipping_department_id = fields.Many2one(
        comodel_name="res.country.department",
        related="partner_shipping_id.department_id",
        string="Shipping Partner's Department",
        store=True,
    )
    partner_shipping_state_id = fields.Many2one(
        comodel_name="res.country.state",
        related="partner_shipping_id.state_id",
        string="Shipping Partner's State",
        store=True,
    )
