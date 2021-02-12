# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    production_request_ids = fields.One2many(
        'mrp.production.request',
        'sale_order_id',
        string="Manufacturing Requests",
    )
    production_request_count = fields.Integer(
        compute='_compute_production_request_count',
        store=True,
        string="Number of Manufacturing Requests",
    )

    @api.depends("production_request_ids")
    def _compute_production_request_count(self):
        for sale in self:
            sale.production_request_count = len(sale.production_request_ids)

    @api.multi
    def action_view_production_request(self):
        action = self.env.ref(
            'mrp_production_request.mrp_production_request_action'
        ).read()[0]
        form = self.env.ref(
            'mrp_production_request.view_mrp_production_request_form'
        )
        if self.production_request_count > 1:
            action['domain'] = [('id', 'in', self.production_request_ids.ids)]
        else:
            action['views'] = [(form.id, 'form')]
            action['res_id'] = self.production_request_ids.id
        return action

    @api.multi
    def action_cancel(self):
        result = super(SaleOrder, self).action_cancel()
        # When a sale person cancel a SO, he might not have the rights to write
        # on MR. But we need the system to create an activity on the MR (so
        # 'write' access), hence the `sudo`.
        self.sudo()._activity_cancel_on_production_request()
        return result

    @api.multi
    def _activity_cancel_on_production_request(self):
        """ If some SO are cancelled, we need to put an activity on their
            generated production requests. We only want one activity to
            be attached.
        """
        for production_request in self.mapped('production_request_ids'):
            production_request.activity_schedule_with_view(
                'mail.mail_activity_data_warning',
                user_id=production_request.assigned_to.id or
                production_request.requested_by.id or self.env.uid,
                views_or_xmlid='sale_mrp_production_request_link.'
                'exception_production_request_on_sale_cancellation',
                render_context={
                    'sale_orders': self,
                }
            )
