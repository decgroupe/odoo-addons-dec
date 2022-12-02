# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_supplier_url = fields.Char(
        string='Product Supplier URL',
        compute="_compute_product_supplier_url",
    )

    @api.depends('partner_id', 'product_id')
    def _compute_product_supplier_url(self):
        for rec in self:
            supplier_info = rec.product_id.seller_ids.filtered(
                lambda s:
                (s.product_id == rec.product_id and s.name == rec.partner_id)
            )
            if not supplier_info:
                supplier_info = rec.product_id.seller_ids.filtered(
                    lambda s: (
                        s.product_tmpl_id == rec.product_id.product_tmpl_id and
                        s.name == rec.partner_id
                    )
                )
            if supplier_info:
                url = supplier_info[0].url or ''
                rec.product_supplier_url = url

    # @api.onchange(
    #     'partner_id',
    #     'product_id',
    # )
    # def _onchange_product_code(self):
    #     for line in self:
    #         supplier_info = line.product_id.seller_ids.filtered(
    #             lambda s:
    #             (s.product_id == line.product_id and s.name == line.partner_id)
    #         )
    #         if not supplier_info:
    #             supplier_info = line.product_id.seller_ids.filtered(
    #                 lambda s: (
    #                     s.product_tmpl_id == line.product_id.product_tmpl_id and
    #                     s.name == line.partner_id
    #                 )
    #             )
    #         if supplier_info:
    #             url = supplier_info[0].url or ''
    #             line.product_supplier_url = url
