# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import fields, models


class MrpSwapProductionLine(models.TransientModel):
    _name = "mrp.swap.production.line"
    _description = "Line for swaping two manufacturing orders"

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        readonly=True,
    )
    from_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="From",
        required=True,
        readonly=True,
    )
    to_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="To",
        required=True,
        readonly=True,
    )
    swap_final_moves = fields.Boolean()
