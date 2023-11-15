# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, fields, models


class SoftwareLicensePass(models.Model):
    _inherit = "software.license.pass"

    product_id = fields.Many2one(
        domain="[('license_pack_id', '!=', False)]",
    )
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        domain="[('partner_id', '=', partner_id)]",
        readonly=True,
        copy=False,
    )
    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Order Line",
        domain="[('order_id', '=', sale_order_id)]",
        readonly=True,
        copy=False,
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.pack_id = self.product_id.license_pack_id
