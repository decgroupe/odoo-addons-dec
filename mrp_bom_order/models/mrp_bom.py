# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import models, api, fields


class MrpBom(models.Model):
    _inherit = "mrp.bom"
    _order = "sequence desc"

    # Override default search order:
    @api.model
    def _bom_find(
        self,
        product_tmpl=None,
        product=None,
        picking_type=None,
        company_id=False
    ):
        """ Finds BoM for particular product, picking and company """
        if product:
            if not product_tmpl:
                product_tmpl = product.product_tmpl_id
            domain = [
                '|', ('product_id', '=', product.id), '&',
                ('product_id', '=', False),
                ('product_tmpl_id', '=', product_tmpl.id)
            ]
        elif product_tmpl:
            domain = [('product_tmpl_id', '=', product_tmpl.id)]
        else:
            # neither product nor template, makes no sense to search
            return False
        if picking_type:
            domain += [
                '|', ('picking_type_id', '=', picking_type.id),
                ('picking_type_id', '=', False)
            ]
        if company_id or self.env.context.get('company_id'):
            domain = domain + [
                (
                    'company_id', '=', company_id or
                    self.env.context.get('company_id')
                )
            ]
        # order to prioritize bom with product_id over the one without
        return self.search(domain, order='sequence desc, product_id', limit=1)
