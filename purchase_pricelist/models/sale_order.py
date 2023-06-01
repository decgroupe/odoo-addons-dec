# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Override sale pricelist field from addons/sale/models/sale.py
    # Lock type to sale using domain attribute
    pricelist_id = fields.Many2one(
        domain="[('type', '=', 'sale'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
