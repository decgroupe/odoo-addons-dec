# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    type = fields.Selection(
        selection=[
            ("sale", "Sale Pricelist"),
            ("purchase", "Purchase Pricelist"),
        ],
        default="sale",
        required=True,
        help="Pricelist Type",
    )

    # fmt: off
    # ruff: noqa: E501
    # Adaptation for purchase from addons/product/models/product_pricelist.py:_get_partner_pricelist_multi
    @api.model
    def _get_partner_pricelist_purchase_multi(self, partner_ids, company_id=None):
        """Retrieve the applicable pricelist for given partners in a given company.

        It will return the first found pricelist in this order:
        First, the pricelist of the specific property (res_id set), this one
                is created when saving a pricelist on the partner form view.
        Else, it will return the pricelist of the partner country group
        Else, it will return the generic property (res_id not set)
        Else, it will return the first available pricelist if any

        :param int company_id: if passed, used for looking up properties,
            instead of current user's company
        :return: a dict {partner_id: pricelist}
        """
        # `partner_ids` might be ID from inactive users. We should use active_test
        # as we will do a search() later (real case for website public user).
        Partner = self.env['res.partner'].with_context(active_test=False)
        company_id = self.env.company.id

        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        Pricelist = self.env['product.pricelist']
        pl_domain = self._get_partner_pricelist_purchase_multi_search_domain_hook(company_id)

        # if no specific property, try to find a fitting pricelist
        result = {}
        remaining_partner_ids = []
        for partner in Partner.browse(partner_ids):
            if partner.specific_property_product_pricelist_purchase._get_partner_pricelist_multi_filter_hook():
                result[partner.id] = partner.specific_property_product_pricelist_purchase
            else:
                remaining_partner_ids.append(partner.id)

        if remaining_partner_ids:
            def convert_to_int(string_value):
                try:
                    return int(string_value)
                except (TypeError, ValueError, OverflowError):
                    return None
            # get fallback pricelist when no pricelist for a given country
            pl_fallback = (
                Pricelist.search(pl_domain + [('country_group_ids', '=', False)], limit=1) or
                # save data in ir.config_parameter instead of ir.default for
                # res.partner.property_product_pricelist_purchase
                # otherwise the data will become the default value while
                # creating without specifying the property_product_pricelist_purchase
                # however if the property_product_pricelist_purchase is not specified
                # the result of the previous line should have high priority
                # when computing
                Pricelist.browse(convert_to_int(IrConfigParameter.get_param(f'res.partner.property_product_pricelist_purchase_{company_id}'))) or
                Pricelist.browse(convert_to_int(IrConfigParameter.get_param('res.partner.property_product_pricelist_purchase'))) or
                Pricelist.search(pl_domain, limit=1)
            )
            # group partners by country, and find a pricelist for each country
            remaining_partners = self.env['res.partner'].browse(remaining_partner_ids)
            partners_by_country = remaining_partners.grouped('country_id')
            for country, partners in partners_by_country.items():
                if not country and (country_code := self.env.context.get('country_code')):
                    country = self.env['res.country'].search([('code', '=', country_code)], limit=1)
                pl = Pricelist.search(pl_domain + [('country_group_ids.country_ids', '=', country.id if country else False)], limit=1)
                pl = pl or pl_fallback
                result.update(dict.fromkeys(partners._ids, pl))

        return result
    # fmt: on

    def _get_partner_pricelist_purchase_multi_search_domain_hook(self, company_id):
        return [
            ("active", "=", True),
            ("company_id", "in", [company_id, False]),
            ("type", "=", "purchase"),
        ]

    def _get_partner_pricelist_multi_search_domain_hook(self, company_id):
        domain = super()._get_partner_pricelist_multi_search_domain_hook(company_id)
        domain.append(("type", "=", "sale"))
        return domain
