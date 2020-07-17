# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models, api


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    # Override sale pricelist field from addons/product/models/res_partner.py
    # Lock type to sale using domain attribute
    property_product_pricelist = fields.Many2one(
        'product.pricelist',
        'Pricelist',
        compute='_compute_product_pricelist',
        inverse="_inverse_product_pricelist",
        company_dependent=False,
        domain=[('type', '=', 'sale')],
        help=
        "This pricelist will be used, instead of the default one, for sales to the current partner"
    )

    # Purchase pricelist field is a dummy copy of the sale pricelist field
    # 'compute' and 'inverse' functions are identical to the sale one
    # excepting that the property name used inside these functions
    property_product_pricelist_purchase = fields.Many2one(
        'product.pricelist',
        'Purchase Pricelist',
        compute='_compute_product_pricelist_purchase',
        inverse="_inverse_product_pricelist_purchase",
        company_dependent=False,
        domain=[('type', '=', 'purchase')],
        help=
        "This pricelist will be used, instead of the default one, for purchases from the current partner"
    )

    @api.multi
    def _compute_product_pricelist_purchase(self):
        Pricelist = self.env['product.pricelist']
        company = self.env.context.get('force_company', False)
        res = Pricelist._get_partner_pricelist_purchase_multi(
            self.ids, company_id=company
        )
        for p in self:
            p.property_product_pricelist_purchase = res.get(p.id)

    @api.one
    def _inverse_product_pricelist_purchase(self):
        Property = self.env['ir.property']
        actual = Property.get(
            'property_product_pricelist_purchase', self._name,
            '%s,%s' % (self._name, self.id)
        )

        # update at each change country, and so erase old pricelist
        if self.property_product_pricelist_purchase or actual:
            # keep the company of the current user before sudo
            Property.with_context(
                force_company=self._context.
                get('force_company', self.env.user.company_id.id)
            ).sudo().set_multi(
                'property_product_pricelist_purchase',
                self._name,
                {self.id: self.property_product_pricelist_purchase},
            )

    def _commercial_fields(self):
        return super(Partner, self)._commercial_fields() + [
            'property_product_pricelist_purchase'
        ]
