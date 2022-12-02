# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import fields, models, api


class RefMarketBomLine(models.Model):
    _name = 'ref.market.bom.line'
    _description = 'Market BoM line'
    _rec_name = "product_id"

    sequence = fields.Integer(
        string='Sequence',
        default=1,
        help="Gives the sequence order when displaying.",
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        related='product_id.product_tmpl_id',
        store=True,
    )
    product_qty = fields.Float(
        string='Product Qty',
        required=True,
        digits='Product UoM',
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Product UOM',
        required=True,
        help="UoM (Unit of Measure) is the unit of measurement for the "
        "inventory control",
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Supplier',
    )
    locked_price = fields.Boolean(
        string='Locked price',
        help="If set, then the price field will be used instead of the "
        "computed price based on supplier pricelist",
    )
    price = fields.Float(
        string='Price',
        digits='Sale Price',
    )
    market_bom_id = fields.Many2one(
        comodel_name='ref.market.bom',
        string='Parent BoM',
        ondelete='cascade',
        required=True,
    )
    activity_name = fields.Char(
        string='Activity Name',
        help="Name of the activity that will be generated",
        oldname="note",
    )

    def _convert_qty_to_hours(self):
        uom_hour = self.env.ref('uom.product_uom_hour')
        if uom_hour and self.product_uom_id.id != uom_hour.id and self.product_uom_id.category_id.id == uom_hour.category_id.id:
            planned_hours = self.product_uom_id._compute_quantity(
                self.product_qty, uom_hour
            )
        else:
            planned_hours = self.product_qty
        return planned_hours
