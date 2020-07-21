# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    locked = fields.Boolean(
        string="Locked",
        copy=False,
        default=False,
        help="This allows the seller to prevent changes by other users."
    )

    @api.multi
    def write(self, vals):
        inter_fields = list(set(self._get_locked_fields()).intersection(vals))
        if inter_fields:
            locked_fields = self.fields_get(inter_fields)
        else:
            locked_fields = []
        for order in self:
            if order.state == 'draft':
                self._check_unlock(vals)
                if inter_fields:
                    self._check_lock_changes(vals, locked_fields)
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
        if self.locked and not 'locked' in vals:
            raise UserError(
                _(
                    '%s is currently locked, you are not allowed to make changes on %s'
                ) % (self.name, ', '.join(translated_fields))
            )

    def _check_unlock(self, vals):
        """Check if someone is trying to unlock a quotation
        """
        self.ensure_one()
        if 'locked' in vals and vals.get('locked') != self.locked:
            allow_lock_change = (self.env.user.id == self.user_id.id)
            if allow_lock_change:
                if vals.get('locked'):
                    msg = _('Locked by {}').format(self.env.user.name)
                else:
                    msg = _('Unlocked by {}').format(self.env.user.name)
                self.message_post(body=msg)
            else:
                raise UserError(
                    _('Only %s is able to lock/unlock this object') %
                    (self.user_id.name)
                )
