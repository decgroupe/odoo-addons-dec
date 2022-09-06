# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    task_ids = fields.One2many(
        'project.task',
        'production_id',
        string='Tasks',
        domain=lambda self: [
            ('|'), ('type_id', '=', False),
            (
                'type_id', '!=',
                self.env.ref('project_identification.time_tracking_type').id
            )
        ],
        readonly=True,
        copy=False,
        help="Tasks generated by this Production Order",
    )

    task_count = fields.Integer(
        compute='_compute_task_count',
        store=True,
        string="Number of Tasks",
    )

    @api.depends("task_ids", "task_ids.type_id")
    def _compute_task_count(self):
        for rec in self:
            rec.task_count = len(rec.task_ids)

    @api.multi
    def action_view_task(self):
        action = self.mapped('task_ids').action_view()
        action['context'] = {}
        return action

    def _create_task_prepare_values(self, bom_line, dict):
        self.ensure_one()
        planned_hours = bom_line._convert_qty_company_hours()
        title = '%s: %s' % (self.name or '', bom_line.display_name)
        description = bom_line.landmark or ''
        return {
            'name': title,
            'planned_hours': planned_hours,
            'partner_id': self.partner_id.id,
            'email_from': self.partner_id.email,
            'description': description,
            'project_id': self.project_id.id,
            'exclude_from_sale_order': True,
            'production_id': self.id,
            'bom_line_id': bom_line.id,
            'company_id': self.company_id.id,
            'user_id': False,  # force non assigned task, as created as sudo()
        }

    @api.multi
    def _create_task(self, bom_line, dict):
        """ Generate task for the given so line, and link it.
            :param project: record of project.project in which the task should be created
            :return task: record of the created task
        """
        values = self._create_task_prepare_values(bom_line, dict)
        task = self.env['project.task'].sudo().create(values)
        self.write({'task_id': task.id})
        # post message on task
        task_msg = _("This task has been created from: ") + (
            "<a href=# data-oe-model=mrp.production data-oe-id=%d>%s</a> (%s)"
        ) % (self.id, self.display_name, bom_line.display_name)
        task.message_post(body=task_msg)
        return task

    @api.multi
    def _action_launch_procurement_rule(self, bom_line, dict):
        self.ensure_one()
        if self.project_id \
        and bom_line.product_id.type == 'service' \
        and bom_line.product_id.service_tracking == 'task_in_project':
            self._create_task(bom_line, dict)
            res = True
        else:
            res = super()._action_launch_procurement_rule(bom_line, dict)
        return res

    @api.multi
    def action_cancel(self):
        result = super().action_cancel()
        self.sudo()._activity_cancel_on_task()
        return result

    @api.multi
    def _activity_cancel_on_task(self):
        """ If some MO are cancelled, we need to put an activity on their
            generated task.
        """
        # purchase_to_notify_map = {
        # }  # map PO -> recordset of POL as {purchase.order: set(mrp.production)}

        # purchase_order_lines = self.env['purchase.order.line'].search(
        #     [
        #         ('id', 'in', self.mapped('purchase_line_ids').ids),
        #         ('state', '!=', 'cancel')
        #     ]
        # )
        # for purchase_line in purchase_order_lines:
        #     purchase_to_notify_map.setdefault(
        #         purchase_line.order_id, self.env['purchase.order.line']
        #     )
        #     purchase_to_notify_map[purchase_line.order_id] |= purchase_line

        # for purchase_order, purchase_lines in purchase_to_notify_map.items():
        #     purchase_order.activity_schedule_with_view(
        #         'mail.mail_activity_data_warning',
        #         user_id=purchase_order.user_id.id or self.env.uid,
        #         views_or_xmlid=
        #         'mrp_purchase.exception_purchase_on_mrp_cancellation',
        #         render_context={
        #             'production_orders': purchase_lines.mapped('production_id'),
        #             'purchase_order_lines': purchase_lines,
        #         }
        #     )
