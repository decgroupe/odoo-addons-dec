# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseOrderSplit(models.TransientModel):
    _name = 'purchase.order.split'
    _description = 'Move purchase order lines to another order'

    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
    )
    order_id = fields.Many2one(
        'purchase.order',
        string='Order Reference',
    )
    origin_order_id = fields.Many2one(
        'purchase.order',
        string='Origin Order',
    )
    order_line_ids = fields.Many2many(
        'purchase.order.line',
        string='Lines',
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        if active_model == 'purchase.order.line' and active_ids:
            order_line_ids = self.env['purchase.order.line'].browse(active_ids)
            origin_order_id = order_line_ids.mapped('order_id')
            partner_id = origin_order_id.mapped('partner_id')
            rec.update(
                {
                    'partner_id': partner_id.id,
                    'origin_order_id': origin_order_id.id,
                    'order_line_ids': [(6, 0, order_line_ids.ids)],
                }
            )
            if len(order_line_ids) == len(origin_order_id.order_line):
                raise UserError(_("You can't select all lines"))
        return rec

    def action_split(self):
        if self.order_id:
            order_id = self.order_id
            self.order_line_ids.write({'order_id': order_id.id})
        elif self.origin_order_id.id:
            order_id = self.origin_order_id.copy(
                {
                    'order_line': [(6, 0, self.order_line_ids.ids)],
                    'group_id': self.origin_order_id.group_id.id,
                    'origin': self.origin_order_id.name,
                }
            )
        action_vals = {
            'name': _('Purchase Orders (after split)'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': order_id.id,
            'res_model': 'purchase.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return action_vals