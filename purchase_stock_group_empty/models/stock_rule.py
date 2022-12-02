# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models, api, _


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _make_po_get_domain(self, values, partner):
        domain = super()._make_po_get_domain(values, partner)
        # Force group_id to False if not set to only group purchase orders
        # without group_id set

        group_id_set = False
        for filter in domain:
            if filter[0] == 'group_id':
                group_id_set = True

        if not group_id_set:
            domain += (('group_id', '=', False), )

        return domain
