# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    allow_timesheets = fields.Boolean(
        string="Allow timesheets",
        default=lambda self: self._default_allow_timesheets(),
    )
    planned_hours = fields.Float(
        string="Planned Hours",
        tracking=True,
    )
    progress = fields.Float(
        compute="_compute_progress_hours",
        aggregator="avg",
        store=True,
        string="Progress",
    )
    remaining_hours = fields.Float(
        compute="_compute_progress_hours",
        readonly=True,
        store=True,
        string="Remaining Hours",
    )
    timesheet_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="production_id",
        string="Timesheet",
    )
    total_hours = fields.Float(
        compute="_compute_total_hours",
        readonly=True,
        store=True,
        string="Total Hours",
    )

    @api.model_create_multi
    def create(self, vals_list):
        # split vals_list in two lists:
        # one with allow_timesheets True, the other False or not set
        allow_timesheets_list = []
        no_allow_timesheets_list = []
        for vals in vals_list:
            if vals.get("allow_timesheets") is True:
                allow_timesheets_list.append(vals)
            else:
                no_allow_timesheets_list.append(vals)
        record_ids = self.env["mrp.production"]
        if no_allow_timesheets_list:
            record_ids |= super(
                MrpProduction, self.with_context(mrp_project_auto_disable=True)
            ).create(no_allow_timesheets_list)
        if allow_timesheets_list:
            record_ids |= super().create(allow_timesheets_list)
        return record_ids

    def write(self, vals):
        res = super().write(vals)
        return res

    @api.model
    def _attach_to_project(self, project_id):
        """Override the _attach_to_project method to set the allow_timesheets field
        when the project_id is set."""
        res = super()._attach_to_project(project_id)
        res["allow_timesheets"] = True
        return res

    @api.model
    def _default_allow_timesheets(self):
        return False

    @api.depends("timesheet_ids", "timesheet_ids.unit_amount")
    def _compute_total_hours(self):
        """Compute the total hours of all timesheets linked to this
        production order. Also set the state to "In Progress" if the production
        order is confirmed and the total hours is greater than 0."""
        for rec in self:
            rec.total_hours = sum(rec.timesheet_ids.mapped("unit_amount"))
            # automatically set state to "In Progress" if a timesheet input
            # is added to this production order
            if rec.total_hours > 0 and rec._allow_auto_start():
                rec.action_start()

    @api.constrains("project_id")
    def _constrains_project_timesheets(self):
        """Update the project_id of all timesheets linked to this production
        order when the project_id is changed."""
        if not self.env.context.get("ignore_constrains_project_timesheets"):
            for rec in self:
                rec.timesheet_ids.update({"project_id": rec.project_id.id})

    @api.depends("planned_hours", "total_hours")
    def _compute_progress_hours(self):
        """Compute the progress of this production order based on the planned
        hours and the total hours of all timesheets linked to this production
        order. Also set the remaining hours to the difference between the
        planned hours and the total hours."""
        for rec in self:
            rec.progress = 0.0
            if rec.planned_hours > 0.0:
                if rec.total_hours > rec.planned_hours:
                    rec.progress = 100
                else:
                    rec.progress = round(100.0 * rec.total_hours / rec.planned_hours, 2)
            rec.remaining_hours = rec.planned_hours - rec.total_hours
