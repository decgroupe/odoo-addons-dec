# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    locked_draft = fields.Boolean(
        string="Locked",
        copy=False,
        default=False,
        help="Prevent changes by users other than the salesperson",
        oldname="locked"
    )

    same_user = fields.Boolean(
        compute='_compute_same_user',
        readonly=True,
    )

    @api.multi
    def action_draft_lock(self):
        for order in self:
            order.locked_draft = True

    @api.multi
    def action_draft_unlock(self):
        for order in self:
            order.locked_draft = False

    @api.multi
    def write(self, vals):
        inter_fields = list(set(self._get_locked_fields()).intersection(vals))
        if inter_fields:
            locked_fields = self.fields_get(inter_fields)
        else:
            locked_fields = []
        for order in self:
            if order.state == 'draft':
                order._check_lock_unlock(vals)
                if inter_fields:
                    order._check_lock_changes(vals, locked_fields)
        res = super().write(vals)
        return res

    def _get_locked_fields(self):
        return [
            'state',
            'user_id',
            'team_id',
            'partner_id',
            'date_order',
            'order_line',
            'sale_order_option_ids',
        ]

    def _check_lock_changes(self, vals, fields):
        """Check if someone is trying to modify a locked quotation
        """
        self.ensure_one()
        translated_fields = [fields[k]['string'] for k in fields]
        if self.locked_draft and not 'locked_draft' in vals:
            raise UserError(
                _(
                    '%s is currently locked, you are not allowed to make changes to %s'
                ) % (self.name, ', '.join(translated_fields))
            )

    def _check_lock_unlock(self, vals):
        """Check if someone is trying to unlock a quotation
        """
        self.ensure_one()
        if 'locked_draft' in vals and vals.get(
            'locked_draft'
        ) != self.locked_draft:
            if vals.get('locked_draft') and not self.user_id:
                raise UserError(
                    _('A salesperson must be set before locking a sale order')
                )
            if self.same_user:
                if vals.get('locked_draft'):
                    msg = _('Locked by {}').format(self.env.user.name)
                else:
                    msg = _('Unlocked by {}').format(self.env.user.name)
                self.message_post(body=msg)
            else:
                raise UserError(
                    _('Only %s is able to lock/unlock this object') %
                    (self.user_id.name)
                )

    @api.multi
    def _compute_same_user(self):
        for order in self:
            order.same_user = (order.user_id == self.env.user)
