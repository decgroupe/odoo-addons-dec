# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from pytz import UTC
from odoo import api, models, fields


class Holidays(models.Model):
    _inherit = "hr.leave"

    def _prepare_timesheet(self, index, max, start, stop):
        self.ensure_one()

        project_id = self.holiday_status_id.timesheet_project_id
        task_id = self.holiday_status_id.timesheet_task_id

        timesheet_description = "%s (%s/%s)" % (
            self.holiday_status_id.name or '', index + 1, max
        )

        return {
            'name': timesheet_description,
            'project_id': project_id.id,
            'task_id': task_id.id,
            'account_id': project_id.analytic_account_id.id,
            'unit_amount': (stop - start).total_seconds() / 3600,
            'user_id': self.employee_id.user_id.id,
            'date_time': fields.Datetime.to_string(start.astimezone(UTC)),
            'holiday_id': self.id,
            'employee_id': self.employee_id.id,
            'company_id': task_id.company_id.id or project_id.company_id.id,
        }

    @api.multi
    def _create_timesheet_with_time(self):
        self.ensure_one()

        # Reuse logic from `list_work_time_per_day` in
        # `odoo/addons/resource/models/resource_mixin.py`

        resource = self.employee_id.resource_id
        calendar = self.employee_id.resource_calendar_id

        from_datetime = fields.Datetime.from_string(self.date_from)
        to_datetime = fields.Datetime.from_string(self.date_to)

        # naive datetimes are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=UTC)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=UTC)

        intervals = calendar._work_intervals(
            from_datetime, to_datetime, resource
        )
        for index, (start, stop, meta) in enumerate(intervals):
            vals = self._prepare_timesheet(index, len(intervals), start, stop)
            self.env['account.analytic.line'].sudo().create(vals)

    def _validate_leave_request(self):
        """ Timesheet will be generated on leave validation only if a timesheet_project_id and a
            timesheet_task_id are set on the corresponding leave type. The generated timesheet will
            be attached to this project/task.
        """
        # Create the timesheet on the vacation project
        for holiday in self.filtered(
                lambda request: request.holiday_type == 'employee' and \
                                request.holiday_status_id.timesheet_project_id and \
                                request.holiday_status_id.timesheet_task_id):
            holiday._create_timesheet_with_time()

        # Track our timesheets for future filtering, we need to it before
        # calling `_validate_leave_request`
        timesheets_with_time = self.sudo().mapped('timesheet_ids')
        # Operate Validate
        res = super(Holidays, self)._validate_leave_request()
        # Get all timesheets
        timesheets_all = self.sudo().mapped('timesheet_ids')
        # Filter only built-in and delete them
        timesheets_builtin = timesheets_all - timesheets_with_time
        timesheets_builtin.write({'holiday_id': False})
        timesheets_builtin.unlink()
        return res
