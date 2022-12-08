# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Field defined in `sale_timesheet_existing_project` module
    project_id = fields.Many2one(copy=False, )

    def _action_confirm(self):
        self.action_create_project()
        res = super(SaleOrder, self)._action_confirm()
        self._sync_project_dates()
        return res

    def _sync_project_dates(self):
        for rec in self.filtered('project_id'):
            rec.project_id.sudo().write({
                'date_start': rec.date_order.date(),
                'date': rec.expected_last_date.date(),
            })

    def _get_create_project_data(self):
        self.ensure_one()
        contract_type_id = self.env.ref('project_identification.contract_type')
        return {
            'name': self.name,
            # Use the same partner than the sale order. The shipping
            # partner is retrieved using `project_partner_location`
            # module and the `partner_shipping_id` field.
            'partner_id': self.partner_id.id,
            'type_id': contract_type_id.id,
            'user_id': self.user_id.id,
        }

    def action_create_project(self):
        Project = self.env['project.project'].with_context(
            # Do not subscribe assigned user
            mail_create_nosubscribe=True,
            # Do not notify the subscribed user (not needed if
            # `mail_create_nosubscribe=True`)
            mail_auto_subscribe_no_notify=True,
        )
        for rec in self:
            if not rec.project_id or self.env.context.get(
                'override_project_id'
            ):
                project_data = rec._get_create_project_data()
                domain = [
                    ('name', '=', project_data['name']),
                    ('partner_id', '=', project_data['partner_id']),
                ]
                if not self.env.context.get('ignore_partner_id'):
                    domain += [('partner_id', '=', project_data['partner_id'])]
                project_id = Project.with_context(active_test=False, ).search(
                    domain, limit=1
                )
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
