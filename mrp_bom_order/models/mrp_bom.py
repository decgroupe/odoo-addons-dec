# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"
    _order = "code asc, sequence desc"

    # Override default search order:
    @api.model
    def _bom_find(
        self,
        product_tmpl=None,
        product=None,
        picking_type=None,
        company_id=False,
        bom_type=False,
    ):
        """Original `_bom_find` method call `search` with an hard-coded `order` value.
        ./addons/mrp/models/mrp_bom.py, so we add a context value to override this with
        our own hard-coded order.
        """
        return super(
            MrpBom, self.with_context(mrp_bom_order_override_search_order=True)
        )._bom_find(
            product_tmpl=product_tmpl,
            product=product,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ Override `order` hard-coded value with our own order
        """
        if self.env.context.get("mrp_bom_order_override_search_order", False) is True:
            order = "sequence desc, product_id"
        res = super(MrpBom, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )
        return res
