# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import fields, models, api
from odoo.tools.progressbar import progressbar as pb


class ResPartner(models.Model):
    _inherit = 'res.partner'

    last_quotation_date = fields.Date(
        string='Last Quotation Date',
        compute='_compute_last_quotation',
        store=True,
    )
    last_sale_date = fields.Date(
        string='Last Sale Date',
        compute='_compute_last_sale',
        store=True,
    )
    last_sale_delivery_date = fields.Date(
        string='Last Sale Delivery',
        compute='_compute_last_delivery',
        store=True,
    )
    shipping_sale_order_ids = fields.One2many(
        comodel_name='sale.order',
        inverse_name='partner_shipping_id',
        string='Sales Order (Shipping)',
    )
    shipping_sale_order_count = fields.Integer(
        compute='_compute_shipping_sale_order_count',
        string='Shipping Sale Order Count',
    )

    def _compute_shipping_sale_order_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search(
            [('id', 'child_of', self.ids)]
        )
        all_partners.read(['parent_id'])

        sale_order_groups = self.env['sale.order'].read_group(
            domain=[('partner_shipping_id', 'in', all_partners.ids)],
            fields=['partner_shipping_id'],
            groupby=['partner_shipping_id']
        )
        for group in pb(sale_order_groups):
            partner = self.browse(group['partner_shipping_id'][0])
            while partner:
                if partner in self:
                    partner.shipping_sale_order_count += group[
                        'partner_shipping_id_count']
                partner = partner.parent_id

    @api.depends('sale_order_ids.date_order', 'sale_order_ids.state')
    def _compute_last_quotation(self):
        """ Get last quotation date """
        SaleOrder = self.env['sale.order']
        for partner in pb(self):
            order = SaleOrder.search(
                [
                    ('partner_id', 'child_of', partner.ids),
                    ('state', 'in', ('draft', 'sent')),
                ],
                limit=1,
                order="date_order desc",
            )
            partner.last_quotation_date = fields.Date.to_date(order.date_order)

    @api.depends('sale_order_ids.date_order', 'sale_order_ids.state')
    def _compute_last_sale(self):
        """ Get last sale date """
        SaleOrder = self.env['sale.order']
        for partner in pb(self):
            order = SaleOrder.search(
                [
                    ('partner_id', 'child_of', partner.ids),
                    ('state', 'not in', ('draft', 'sent', 'cancel')),
                ],
                limit=1,
                order="date_order desc",
            )
            partner.last_sale_date = fields.Date.to_date(order.date_order)

    @api.depends(
        'shipping_sale_order_ids.effective_last_date',
        'shipping_sale_order_ids.state'
    )
    def _compute_last_delivery(self):
        """ Get last sale delivery/shipping date """
        SaleOrder = self.env['sale.order']
        for partner in pb(self):
            order = SaleOrder.search(
                [
                    ('partner_shipping_id', 'child_of', partner.ids),
                    ('state', 'not in', ('draft', 'sent', 'cancel')),
                    ('effective_last_date', '!=', False),
                ],
                limit=1,
                order="effective_last_date desc",
            )
            partner.last_sale_delivery_date = order.effective_last_date

    def action_open_shipping_sale_orders(self):
        action = self.env.ref('sale.act_res_partner_2_sale_order').read()[0]
        action['domain'] = [
            ('id', 'in', self.mapped('shipping_sale_order_ids').ids),
        ]
        action['context'] = {}
        return action
