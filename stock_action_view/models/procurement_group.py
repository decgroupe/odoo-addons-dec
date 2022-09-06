# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import models, api, _


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def action_view_base(self):
        return {
            'name': _('Procurement Group(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'procurement.group',
            'target': 'current',
        }

    @api.multi
    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action['domain'] = [('id', 'in', self.ids)]
        else:
            form = self.env.ref('stock.procurement_group_form_view')
            action['views'] = [(form.id, 'form')]
            action['res_id'] = self.ids[0]
        return action
