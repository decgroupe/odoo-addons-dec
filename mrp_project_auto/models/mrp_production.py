# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, values):
        production_id = super(MrpProduction, self).create(values)
        # Do not call `action_create_project` here since it will be probably
        # too late, instead, we override `_generate_moves` to call it before
        # generating any moves
        return production_id

    @api.multi
    def _generate_moves(self):
        if not self.env.context.get("mrp_project_auto_disable"):
            # Project must be created before any moves to be propagated
            # to sub-production.
            self.action_create_project()
        res = super()._generate_moves()
        return res

    @api.multi
    def action_create_project(self):
        time_tracking_type_id = self.env.ref(
            'project_identification.time_tracking_type'
        )
        Project = self.env['project.project']
        created_project_ids = self.env['project.project']
        for rec in self:
            if not rec.project_id or self.env.context.get(
                'override_project_id'
            ):
                rec.allow_timesheets = True
                sale_order_id = rec.sale_order_id
                if sale_order_id:
                    project_data = {
                        'name': sale_order_id.name,
                        # Use the same partner than the sale order. The shipping
                        # partner is retrieved using `project_partner_location`
                        # module and the `partner_shipping_id` field.
                        'partner_id': sale_order_id.partner_id.id,
                    }
                else:
                    project_data = {
                        'name': rec.name,
                        'partner_id': rec.partner_id.id,
                    }
                project_data['type_id'] = time_tracking_type_id.id
                project_id = Project.search(
                    [
                        ('name', '=', project_data['name']),
                        ('partner_id', '=', project_data['partner_id']),
                    ],
                    limit=1
                )
                if not project_id:
                    # Create project as SUPER_USER
                    project_id = Project.sudo().create(project_data)
                    created_project_ids += project_id
                rec.project_id = project_id
        # Set a default analytic parent account but only for projects created
        # from this function
        if created_project_ids:
            analytic_account_ids = created_project_ids.mapped('analytic_account_id')
            analytic_account_ids.write(
                {'parent_id': self.env.ref('mrp_project.analytic_production').id}
            )
