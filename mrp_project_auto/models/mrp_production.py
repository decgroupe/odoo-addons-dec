# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, values):
        production_id = super(MrpProduction, self).create(values)
        production_id.action_create_project()
        return production_id

    @api.multi
    def action_create_project(self):
        time_tracking_type_id = self.env.ref(
            'project_identification.time_tracking_type'
        )
        for rec in self:
            if not rec.project_id or self.env.context.get(
                'override_project_id'
            ):
                rec.allow_timesheets = True
                sale_order_id = rec.sale_order_id
                if sale_order_id:
                    project_data = {
                        'name': sale_order_id.name,
                        'partner_id': sale_order_id.partner_shipping_id.id,
                    }
                else:
                    project_data = {
                        'name': rec.name,
                        'partner_id': rec.partner_id.id,
                    }
                project_data['type_id'] = time_tracking_type_id.id
                project_id = self.env['project.project'].search(
                    [
                        ('name', '=', project_data['name']),
                        ('partner_id', '=', project_data['partner_id']),
                        ('type_id', '=', project_data['type_id']),
                    ],
                    limit=1
                )
                if not project_id:
                    # Create project as SUPER_USER
                    project_id = self.env['project.project'].sudo(
                    ).create(project_data)
                rec.project_id = project_id
        self.update_project_analytic_account()

    @api.multi
    def update_project_analytic_account(self):
        analytic_account_ids = self.filtered('project_id')\
            .mapped('project_id').mapped('analytic_account_id')
        analytic_account_ids.write(
            {'parent_id': self.env.ref('mrp_project.analytic_production').id}
        )
