# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2024

from odoo import models, api, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    # the purpose of this field is to reintroduce the logic implemented in OCA module
    # `sale_timesheet_task_exclude` in Odoo < 14
    # note that if looks like the existing `non_allow_billable`, but this field is
    # only visible if pricing_type=employee_rate and bill_type=customer_task
    exclude_from_sale_order = fields.Boolean(
        string="Non-billable (excluded from order)",
        default=True,
        help=(
            "Checking this would exclude this task to be automatically linked "
            "to a sale line"
        ),
    )
    # convert related field to compute
    allow_billable = fields.Boolean(
        compute="_compute_allow_billable",
        related=None,
    )

    @api.depends("project_id.contract_ids")
    def _compute_sale_order_id(self):
        task_ids = self
        for task in self:
            if len(task.project_id.contract_ids) == 1:
                contract_id = task.project_id.contract_ids
                task.sale_order_id = contract_id
                # like built-in compute, assign partner from sale order
                if not task.partner_id:
                    task.partner_id = task.sale_order_id.partner_id
                task_ids -= task
        # call default compute on unprocessed tasks
        return super(ProjectTask, task_ids)._compute_sale_order_id()

    def _compute_sale_line(self):
        """Override compute function from `sale_project` and `sale_timesheet` to disable
        automatic editing of partner_id, sale_order_id, sale_line_id"""
        task_ids = self.filtered(lambda t: not t.exclude_from_sale_order)
        return super(ProjectTask, task_ids)._compute_sale_line()

    @api.depends(
        "exclude_from_sale_order",
        "project_id.allow_billable",
    )
    def _compute_allow_billable(self):
        for rec in self:
            if rec.exclude_from_sale_order:
                rec.allow_billable = False
            else:
                # retrieve built-in behaviour
                rec.allow_billable = rec.project_id.allow_billable

    def write(self, vals):
        if vals.get("exclude_from_sale_order") is True:
            # unset existing links mostly set from inherited `_compute_sale_line`
            vals["sale_order_id"] = False
            vals["sale_line_id"] = False
        return super().write(vals)
