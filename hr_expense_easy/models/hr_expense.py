# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import _, api, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.multi
    def action_duplicate(self):
        self.ensure_one()
        self.copy(default={
            'sheet_id': self.sheet_id.id,
        })

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        if self.attachment_number == 0:
            res = self.action_create_attachment_view()
        else:
            res = super().action_get_attachment_view()
        return res

    @api.multi
    def action_create_attachment_view(self):
        self.ensure_one()
        context = {'default_res_model': self._name, 'default_res_id': self.id}
        domain = [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
        return {
            'name': _('Create attachment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': "ir.attachment",
            'context': context,
            'domain': domain,
        }
