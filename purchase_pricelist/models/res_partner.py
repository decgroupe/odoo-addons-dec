# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    # Override sale pricelist field from addons/product/models/res_partner.py
    # Lock type to sale using domain attribute
    property_product_pricelist = fields.Many2one(
        domain=lambda self: [
            ("type", "=", "sale"),
            ("company_id", "in", (self.env.company.id, False)),
        ],
    )

    # Purchase pricelist field is a dummy copy of the sale pricelist field
    # 'compute' and 'inverse' functions are identical to the sale one excepting the
    # property name used inside these functions
    property_product_pricelist_purchase = fields.Many2one(
        comodel_name="product.pricelist",
        string="Purchase Pricelist",
        compute="_compute_product_pricelist_purchase",
        inverse="_inverse_product_pricelist_purchase",
        company_dependent=False,
        domain=lambda self: [
            ("type", "=", "purchase"),
            ("company_id", "in", (self.env.company.id, False)),
        ],
        help="This pricelist will be used, instead of the default one, for purchases "
        "from the current partner",
    )

    def _compute_product_pricelist_purchase(self):
        company = self.env.company.id
        res = self.env["product.pricelist"]._get_partner_pricelist_purchase_multi(
            self.ids, company_id=company
        )
        for p in self:
            p.property_product_pricelist_purchase = res.get(p.id)

    def _inverse_product_pricelist_purchase(self):
        for partner in self:
            Property = self.env["ir.property"]
            actual = Property._get(
                "property_product_pricelist_purchase",
                partner._name,
                "%s,%s" % (partner._name, partner.id),
            )

            # update at each change country, and so erase old pricelist
            if partner.property_product_pricelist_purchase or actual:
                # keep the company of the current user before sudo
                Property.with_company(partner.company_id).sudo()._set_multi(
                    "property_product_pricelist_purchase",
                    partner._name,
                    {partner.id: partner.property_product_pricelist_purchase},
                )

    def _commercial_fields(self):
        return super(Partner, self)._commercial_fields() + [
            "property_product_pricelist_purchase"
        ]
