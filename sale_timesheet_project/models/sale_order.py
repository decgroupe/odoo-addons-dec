# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one(copy=False, )

    @api.multi
    def _action_confirm(self):
        self.action_create_project()
        res = super(SaleOrder, self)._action_confirm()
        return res

    @api.multi
    def action_create_project(self):
        contract_type_id = self.env.ref('project_identification.contract_type')
        Project = self.env['project.project'].with_context(active_test=False)
        for rec in self:
            if not rec.project_id or self.env.context.get(
                'override_project_id'
            ):
                project_data = {
                    'name': rec.name,
                    'partner_id': rec.partner_shipping_id.id,
                    'type_id': contract_type_id.id,
                    'user_id': rec.user_id.id,
                }
                domain = [
                    ('name', '=', project_data['name']),
                    ('partner_id', '=', project_data['partner_id']),
                ]
                if not self.env.context.get('ignore_partner_id'):
                    domain += [('partner_id', '=', project_data['partner_id'])]
                project_id = Project.search(domain, limit=1)
                if not project_id:
                    # Create project as SUPER_USER
                    project_id = Project.sudo().create(project_data)
                rec.project_id = project_id
            # Assign same analytic account
            rec.analytic_account_id = rec.project_id.analytic_account_id

    @api.depends('project_id')
    def _compute_visible_project(self):
        super()._compute_visible_project()
        for order in self.filtered(lambda x: not x.visible_project):
            if order.project_id:
                order.visible_project = True
