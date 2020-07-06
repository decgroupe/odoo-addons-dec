# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Jul 2020

from odoo import api, fields, models, _


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    user_id = fields.Many2one(
        'res.users',
        string='Mapped to',
    )

    production_ids = fields.One2many(
        'mrp.production',
        'assigned_workcenter_id',
        "Production Orders",
    )

    production_count = fields.Integer(
        compute='_compute_production_order',
        string='Production count',
        default=0,
        store=False,
    )

    @api.multi
    @api.depends("production_ids")
    def _compute_production_order(self):
        for workcenter in self:
            workcenter.production_count = len(workcenter.production_ids)

    @api.multi
    def write(self, vals):
        if vals.get('user_id') and not 'name' in vals:
            Users = self.env['res.users']
            for workcenter in self:
                user_name = Users.browse(vals['user_id']).name
                if workcenter.name != Users.browse(vals['user_id']).name:
                    workcenter.name = user_name
        res = super().write(vals)
        return res

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            values = {
                'name': self.user_id.name,
            }
            self.update(values)
