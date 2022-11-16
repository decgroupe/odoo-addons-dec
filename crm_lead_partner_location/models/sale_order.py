# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2022

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields):
        # Note that this code is finally useless because shipping field is
        # overriden in the `onchange_partner_id` event.
        # Take a look on the `address_get` function in `res_partner.py`
        result = super(SaleOrder, self).default_get(fields)
        opportunity_id = self.env["crm.lead"].browse(
            result.get("opportunity_id", False)
        )
        if opportunity_id and opportunity_id.partner_shipping_id:
            result['partner_shipping_id'
                  ] = opportunity_id.partner_shipping_id.id
        return result
