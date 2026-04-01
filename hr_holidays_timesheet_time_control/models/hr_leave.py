# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

import logging

from pytz import UTC

from odoo import fields, models

_logger = logging.getLogger(__name__)


class Holidays(models.Model):
    _inherit = "hr.leave"

    def _prepare_timesheet(self, index, count, start, stop, project, task):
        """Prepare vals to create a timesheet line for a single work interval."""
        self.ensure_one()
        timesheet_description = (
            f"{self.holiday_status_id.name or ''} ({index + 1}/{count})"
        )
        return {
            "name": timesheet_description,
            "project_id": project.id,
            "task_id": task.id,
            "account_id": project.sudo().account_id.id,
            "unit_amount": (stop - start).total_seconds() / 3600,
            "user_id": self.employee_id.user_id.id,
            "date": start.astimezone(UTC).date(),
            "date_time": fields.Datetime.to_string(start.astimezone(UTC)),
            "holiday_id": self.id,
            "employee_id": self.employee_id.id,
            "company_id": task.sudo().company_id.id or project.sudo().company_id.id,
        }

    def _generate_timesheets(self, ignored_resource_calendar_leaves=None):
        """Generate timesheets with precise time intervals from the working calendar.

        Overrides the default implementation to create one timesheet line per
        work interval with the actual start datetime in the `date_time` field,
        instead of one line per day with only daily totals.
        """
        self_no_ts = self.filtered(lambda r: not r.holiday_status_id.timesheet_generate)
        res = super(Holidays, self_no_ts)._generate_timesheets(
            ignored_resource_calendar_leaves=ignored_resource_calendar_leaves
        )
        vals_list = []
        leave_ids = []
        self_ts = self - self_no_ts
        for leave in self_ts:
            # resolve project and task from leave type or company defaults
            if leave.holiday_status_id.company_id:
                project = leave.holiday_status_id.timesheet_project_id
                task = leave.holiday_status_id.timesheet_task_id
            else:
                project = leave.employee_id.company_id.internal_project_id
                task = leave.employee_id.company_id.leave_timesheet_task_id
            if not project or not task:
                continue
            leave_ids.append(leave.id)
            if not leave.employee_id:
                continue
            resource = leave.employee_id.resource_id
            calendar = leave.employee_id.resource_calendar_id
            from_datetime = leave.date_from
            to_datetime = leave.date_to
            # ensure timezone-aware datetimes
            if not from_datetime.tzinfo:
                from_datetime = from_datetime.replace(tzinfo=UTC)
            if not to_datetime.tzinfo:
                to_datetime = to_datetime.replace(tzinfo=UTC)
            # compute leaves is not enabled otherwise a second generation would not
            # re-create entries whereas older one would be unlinked, leading to missing
            # timesheets
            intervals = list(
                calendar._work_intervals_batch(
                    from_datetime, to_datetime, resource, compute_leaves=False
                )[resource.id]
            )
            if not intervals:
                _logger.warning(
                    "No work interval found for leave %s, employee %s and calendar %s",
                    leave.id,
                    leave.employee_id.name,
                    calendar.name,
                )
            for index, (start, stop, _meta) in enumerate(intervals):
                vals_list.append(
                    leave._prepare_timesheet(
                        index, len(intervals), start, stop, project, task
                    )
                )
        # unlink previous timesheets to avoid duplicates (needed when regenerating)
        if leave_ids:
            old_timesheets = (
                self.env["account.analytic.line"]
                .sudo()
                .search([("project_id", "!=", False), ("holiday_id", "in", leave_ids)])
            )
            if old_timesheets:
                old_timesheets.holiday_id = False
                old_timesheets.unlink()
        self.env["account.analytic.line"].sudo().create(vals_list)
        return res
