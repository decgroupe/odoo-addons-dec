# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Aug 2020

from odoo import api, fields, models, _


class MrpProductionRequest(models.Model):
    _inherit = 'mrp.production.request'

    production_name = fields.Char(
        string='Prefix',
        readonly=True,
    )
    use_common_procurement_group = fields.Boolean(
        string='Use Common Procurement Group',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'to_approve': [('readonly', False)],
        },
        help='If checked, when the first manufacturing order is created '
        'a procurement order is first created based on the MO sequence. '
    )
    common_procurement_group_id = fields.Many2one(
        string='Common Procurement Group',
        comodel_name='procurement.group',
        copy=False,
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'to_approve': [('readonly', False)],
        },
    )

    @api.model
    def _create_sequence(self, vals):
        res_vals = super()._create_sequence(vals)
        if not vals.get('name') or vals.get('name') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'mrp.production.request') or '/'
        return vals
