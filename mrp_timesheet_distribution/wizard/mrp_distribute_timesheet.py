# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import logging
from datetime import datetime, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MrpDistributeTimesheet(models.TransientModel):
    _name = "mrp.distribute.timesheet"
    _description = "Distribute working time along multiple production orders"

    @api.model
    def _default_date_time(self):
        def ceil_dt(dt, delta):
            return dt + (datetime.min - dt) % delta

        return ceil_dt(fields.Datetime.now(), timedelta(minutes=-15))

    @api.model
    def _default_reason(self):
        return self.env.ref("mrp_timesheet_distribution.layout_and_wiring")

    production_ids = fields.Many2many(
        comodel_name="mrp.production",
        string="Production Orders",
        readonly=True,
    )
    reason_id = fields.Many2one(
        comodel_name="mrp.distribute.timesheet.reason",
        string="Reason",
        required=True,
        default=_default_reason,
    )
    custom_reason = fields.Char(string="Other Reason")
    date_time = fields.Datetime(
        default=_default_date_time,
        required=True,
    )
    unit_amount = fields.Float(
        string="Quantity",
        default=0.0,
        required=True,
    )
    timesheet_line_ids = fields.Many2many(
        comodel_name="mrp.distribute.timesheet.line",
        string="Timesheet Lines",
        compute="_compute_timesheet_line_ids",
    )

    exclude_time = fields.Boolean()
    excluded_start_time = fields.Datetime()
    excluded_end_time = fields.Datetime()

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_ids = self._context.get("active_ids")
        active_model = self._context.get("active_model")

        if active_model == "mrp.production" and active_ids:
            production_ids = self.env["mrp.production"].browse(active_ids)
            rec.update({"production_ids": production_ids.ids})
        return rec

    def action_reopen(self):
        return self._reopen()

    def _reopen(self, id=False):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "res_id": id or self.id,
            "res_model": self._name,
            "target": "new",
            "context": {
                "default_model": self._name,
            },
        }

    def action_distribute(self):
        self._do_distribute()

    def action_distribute_continue(self):
        self._do_distribute()
        mrp_distribute_timesheet_id = self.create(
            {
                "date_time": self.timesheet_line_ids[-1].end_time,
                "reason_id": self.reason_id.id,
                "exclude_time": self.exclude_time,
                "production_ids": [(6, 0, self.production_ids.ids)],
            }
        )
        mrp_distribute_timesheet_id.onchange_date_time()
        return self._reopen(mrp_distribute_timesheet_id.id)

    @api.onchange("date_time")
    def onchange_date_time(self):
        # Convert datetime into user timezone to manipulate hours and minutes
        tz = self.env.context.get("tz") or self.env.user.tz
        date_time_tz = pytz.timezone(tz).normalize(pytz.utc.localize(self.date_time))

        resource_calendar_id = self.env.user.resource_calendar_id
        attendance_ids = resource_calendar_id.attendance_ids.filtered(
            lambda r: r.dayofweek == str(self.date_time.weekday())
        )

        st = et = False
        for attendance_id in attendance_ids:
            if attendance_id.day_period == "morning":
                hour, minute = divmod(float(attendance_id.hour_to) * 60, 60)
                st = date_time_tz.replace(
                    hour=round(hour), minute=round(minute), second=0
                )
            if attendance_id.day_period == "afternoon":
                hour, minute = divmod(float(attendance_id.hour_from) * 60, 60)
                et = date_time_tz.replace(
                    hour=round(hour), minute=round(minute), second=0
                )

        # Set start and end time in user timezone
        if not st or not et:
            st = date_time_tz.replace(hour=12, minute=0, second=0)
            et = date_time_tz.replace(hour=13, minute=30, second=0)

        # Convert back data to UTC since all datetime data must be
        # stored without timezone info (means UTC)
        self.excluded_start_time = pytz.utc.normalize(st).replace(tzinfo=None)
        self.excluded_end_time = pytz.utc.normalize(et).replace(tzinfo=None)

    @api.depends(
        "date_time",
        "unit_amount",
        "exclude_time",
        "excluded_start_time",
        "excluded_end_time",
    )
    def _compute_timesheet_line_ids(self):
        self.timesheet_line_ids.unlink()
        if self.production_ids and self.date_time and self.unit_amount:
            start = self.date_time
            end = start + timedelta(hours=self.unit_amount)

            if (
                self.exclude_time
                and self.excluded_end_time > start >= self.excluded_start_time
            ):
                start = self.excluded_end_time
                end = start + timedelta(hours=self.unit_amount)
                self._generate_timesheet_interval(start, end)
            elif (
                self.exclude_time
                and end > self.excluded_start_time
                and start < self.excluded_end_time
            ):
                start_delta = self.excluded_start_time - start
                self._generate_timesheet_interval(start, start + start_delta)
                self._generate_timesheet_interval(
                    self.excluded_end_time,
                    self.excluded_end_time
                    + timedelta(hours=self.unit_amount)
                    - start_delta,
                )
            else:
                self._generate_timesheet_interval(start, end)

    def _generate_timesheet_interval(self, start, end):
        diff = (end - start) / len(self.production_ids)
        i = 0
        line_ids = self.env["mrp.distribute.timesheet.line"]
        for production_id in self.production_ids:
            vals = {
                "start_time": i * diff + start,
                "end_time": (i + 1) * diff + start,
                "project_id": production_id.project_id.id,
                "production_id": production_id.id,
            }
            line_ids += self.env["mrp.distribute.timesheet.line"].create(vals)
            i += 1
        self.timesheet_line_ids += line_ids

    @api.model
    def _get_or_create_task(self, project_id, name):
        time_tracking_type = self.env.ref("project_identification.time_tracking_type")
        stage_done = self.env.ref("project_task_default_stage.project_tt_deployment")
        task_id = self.env["project.task"].search(
            [
                ("project_id", "=", project_id.id),
                ("name", "=", name),
            ],
            limit=1,
        )
        if not task_id:
            vals = {
                "project_id": project_id.id,
                "type_id": time_tracking_type.id,
                "stage_id": stage_done.id,
                "name": name,
            }
            task_id = self.env["project.task"].create(vals)
        return task_id

    def _do_distribute(self):
        if not self.timesheet_line_ids:
            raise ValidationError(_("The number of timesheet lines cannot be 0."))

        for line_id in self.timesheet_line_ids:
            name = self.reason_id.name
            if self.reason_id == self.env.ref("mrp_timesheet_distribution.other"):
                name = self.custom_reason

            vals_line = line_id._prepare_analytic_line(name)
            if not "task_id" in vals_line:
                vals_line["task_id"] = self._get_or_create_task(
                    line_id.project_id, name
                ).id

            self.env["account.analytic.line"].create(vals_line)
