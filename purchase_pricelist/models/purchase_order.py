# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Mimic pricelist_id field from sale.order model
    # Lock type to purchase using domain attribute
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        required=False,
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
        domain=[('type', '=', 'purchase')],
        help="Pricelist for current purchase order."
    )

    @api.model
    def create(self, vals):
        # Make sure 'pricelist_id' is defined
        if any(f not in vals for f in ['pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            vals['pricelist_id'] = vals.setdefault(
                'pricelist_id', partner.property_product_pricelist and
                partner.property_product_pricelist.id
            )
        return super().create(vals)

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        # Assign purchase pricelist from the partner property field
        if self.partner_id:
            values = {
                'pricelist_id':
                    self.partner_id.property_product_pricelist_purchase and
                    self.partner_id.property_product_pricelist_purchase.id
                    or False,
            }
            self.update(values)


    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self):
        self.action_recompute_all_lines()

    def action_recompute_all_lines(self):
        for order in self:
            for line in order.order_line:
                line._onchange_quantity()
