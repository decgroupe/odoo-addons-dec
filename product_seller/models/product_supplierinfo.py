# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo import models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    def _get_filtered_supplier(self, company_id, product_id, params=False):
        if product_id._name == "product.template":
            # Filter only active partners and matching product template
            # (copy from product variant _get_filtered_sellers)
            res = self.filtered(
                lambda s: (not s.company_id or s.company_id.id == company_id.id)
                and (
                    s.partner_id.active
                    and (not s.product_tmpl_id or s.product_tmpl_id == product_id)
                )
            )
        else:
            res = super()._get_filtered_supplier(company_id, product_id, params=params)
        return res
