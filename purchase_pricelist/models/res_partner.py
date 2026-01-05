# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class Partner(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    # Override sale pricelist field from ./odoo/addons/product/models/res_partner.py
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
    # when the specific_property_product_pricelist_purchase is not defined
    # the fallback value may be computed with 2 ir.config_parameter
    # in self.env['product.pricelist']._get_partner_pricelist_purchase_multi
    # 1. res.partner.property_product_pricelist_purchase_{company_id}  # current company
    # 2. res.partner.property_product_pricelist_purchase               # all companies
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

    # the specific pricelist to compute property_product_pricelist_purchase
    # this company dependent field shouldn't have any fallback in ir.default
    specific_property_product_pricelist_purchase = fields.Many2one(
        comodel_name="product.pricelist",
        company_dependent=True,
    )

    @api.depends("country_id", "specific_property_product_pricelist_purchase")
    @api.depends_context("company", "country_code")
    def _compute_product_pricelist_purchase(self):
        company = self.env.company.id
        res = self.env["product.pricelist"]._get_partner_pricelist_purchase_multi(
            self.ids, company_id=company
        )
        for partner in self:
            partner.property_product_pricelist_purchase = res.get(partner.id)

    def _inverse_product_pricelist_purchase(self):
        for partner in self:
            pls = self.env["product.pricelist"].search(
                [
                    (
                        "country_group_ids.country_ids.code",
                        "=",
                        partner.country_id and partner.country_id.code or False,
                    )
                ],
                limit=1,
            )
            default_for_country = pls
            actual = partner.specific_property_product_pricelist_purchase
            # update at each change country, and so erase old pricelist
            if partner.property_product_pricelist_purchase or (
                actual and default_for_country and default_for_country.id != actual.id
            ):
                partner.specific_property_product_pricelist_purchase = (
                    False
                    if partner.property_product_pricelist_purchase.id
                    == default_for_country.id
                    else partner.property_product_pricelist_purchase.id
                )

    def _commercial_fields(self):
        return [
            *super()._commercial_fields(),
            "specific_property_product_pricelist_purchase",
        ]
