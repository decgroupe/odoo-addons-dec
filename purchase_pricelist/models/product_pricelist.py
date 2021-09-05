# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    type = fields.Selection(
        [
            ('sale', 'Sale Pricelist'),
            ('purchase', 'Purchase Pricelist'),
        ],
        default='sale',
        required=True,
        help='Pricelist Type'
    )

    # Adaptation for purchase from addons/product/models/product_pricelist.py
    def _get_partner_pricelist_purchase(self, partner_id, company_id=None):
        """ Retrieve the applicable pricelist for a given partner in a given company.

            :param company_id: if passed, used for looking up properties,
             instead of current user's company
        """
        res = self._get_partner_pricelist_multi([partner_id], company_id)
        return res[partner_id].id

    # Adaptation for purchase from addons/product/models/product_pricelist.py
    def _get_partner_pricelist_purchase_multi(
        self, partner_ids, company_id=None
    ):
        """ Retrieve the applicable pricelist for given partners in a given company.

            It will return the pricelist of the specific property (res_id set),
            this one is created when saving a pricelist on the partner form view.

            :param company_id: if passed, used for looking up properties,
                instead of current user's company
            :return: a dict {partner_id: pricelist}
        """
        # `partner_ids` might be ID from inactive users. We should use active_test
        # as we will do a search() later (real case for website public user).
        Partner = self.env['res.partner'].with_context(active_test=False)
        Property = self.env['ir.property'].with_context(
            force_company=company_id or self.env.user.company_id.id
        )
        # if no specific property, try to find a fitting pricelist
        result = Property.get_multi(
            'property_product_pricelist_purchase', Partner._name, partner_ids
        )
        return result