# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrderMerge(models.TransientModel):
    _name = 'purchase.order.merge'
    _description = 'Merge Purchase Order'

    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
    )
    order_id = fields.Many2one(
        'purchase.order',
        'Purchase Order',
    )
    origin_order_ids = fields.Many2many(
        'purchase.order',
        string='Origin Orders',
        readonly=True,
    )
    pre_process = fields.Selection(
        [
            ('create', 'Create new order'),
            ('merge', 'Merge orders on selected order'),
        ],
        string="Merge Mode",
        default='create'
    )
    post_process = fields.Selection(
        [
            ('cancel', 'Cancel'),
            ('delete', 'Delete'),
        ],
        string="Remaining Order(s)",
        default='cancel'
    )

    def _check_selection_count(self, order_ids):
        if len(order_ids) < 2:
            raise UserError(
                _("Please select two or more orders in the list view")
            )

    def _check_selection_state(self, order_ids):
        PurchaseOrder = self.env['purchase.order']
        selection_states = order_ids.mapped('state')
        mergeable_states = PurchaseOrder._get_mergeable_states()
        diff_states = set(selection_states) - set(mergeable_states)
        if diff_states:
            display_states = {}
            # Get human readable incompatible state names
            for state in diff_states:
                display_state = dict(
                    PurchaseOrder._fields['state']._description_selection(
                        self.env
                    )
                ).get(state)
                display_states[state] = display_state
            invalid_po = []
            for order_id in order_ids.filtered(
                lambda p: p.state in diff_states
            ):
                invalid_po.append(
                    '{} state is {}'.format(
                        order_id.display_name, display_states[order_id.state]
                    )
                )

            raise UserError(
                _("Selection contains order(s) in incompatible states:\n%s") %
                ('\n - '.join([''] + invalid_po))
            )

    def _check_selection_partners(self, order_ids):
        partner_ids = order_ids.mapped('partner_id')
        if len(partner_ids) > 1:
            raise UserError(
                _(
                    "All orders must have the same supplier.\n"
                    "You have selected orders from these partners:\n%s"
                ) % ('\n - '.join([''] + partner_ids.mapped('display_name')))
            )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        if active_model == 'purchase.order' and active_ids:
            origin_order_ids = self.env['purchase.order'].browse(active_ids)
            # Ensure selected data is valid
            self._check_selection_count(origin_order_ids)
            self._check_selection_state(origin_order_ids)
            self._check_selection_partners(origin_order_ids)
            # Assign wizard default values
            partner_id = origin_order_ids.mapped('partner_id')
            rec.update(
                {
                    'partner_id': partner_id.id,
                    'origin_order_ids': [(6, 0, origin_order_ids.ids)],
                }
            )
        return rec

    # @api.onchange('post_process')
    # def onchange_post_process(self):
    #     res = {}
    #     for wizard in self:
    #         wizard.order_id = False
    #         if wizard.post_process in ['cancel', 'delete']:
    #             res['domain'] = {
    #                 'order_id': [('id', 'in', self.origin_order_ids.ids)]
    #             }
    #         return res

    def _try_merging(self, line):
        match_line = False
        if self.order_id.order_line:
            for po_line in self.order_id.order_line:
                if line.product_id == po_line.product_id and \
                        line.price_unit == po_line.price_unit:
                    match_line = po_line
                    break
        if match_line:
            match_line.product_qty += line.product_qty
            po_taxes = [tax.id for tax in match_line.taxes_id]
            [po_taxes.append((tax.id)) for tax in line.taxes_id]
            match_line.taxes_id = [(6, 0, po_taxes)]
            return True
        else:
            return False

    def _pre_process_create(self):
        self.order_id = self.env['purchase.order'].with_context(
            {
                'trigger_onchange': True,
                'onchange_fields_to_trigger': [self.partner_id]
            }
        ).create({'partner_id': self.partner_id})
        self.pre_process_merge()

    def _pre_process_merge(self):
        default = {'order_id': self.order_id.id}
        # Remove selected order from list
        self.origin_order_ids -= self.order_id
        for order in self.origin_order_ids:
            for line in order.order_line:
                merged = self._try_merging(line, self.order_id)
                if not merged:
                    line.copy(default=default)

    def _post_process_cancel(self):
        for order_id in self.origin_order_ids:
            order_id.button_cancel()

    def _post_process_delete(self):
        self.post_process_cancel()
        for order_id in self.origin_order_ids:
            order_id.sudo().unlink()

    @api.multi
    def action_merge(self):
        if self.pre_process == 'create':
            self._pre_process_create()
        elif self.pre_process == 'merge':
            self._pre_process_merge()

        if self.post_process == 'cancel':
            self._post_process_cancel()
        elif self.post_process == 'delete':
            self._post_process_delete()
