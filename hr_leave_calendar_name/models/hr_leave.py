# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import _, models


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    def _prepare_holidays_meeting_values(self):
        """Hook original method result to customize meeting name"""
        meetings_values_for_user_id = super()._prepare_holidays_meeting_values()
        for user_id, meetings_values in meetings_values_for_user_id.items():
            for meeting_values in meetings_values:
                holiday = self.browse(meeting_values["res_id"])
                if holiday.leave_type_request_unit == "hour":
                    unit = _("%.2f hour(s)") % (holiday.number_of_hours_display)
                else:
                    unit = _("%.2f day(s)") % (holiday.number_of_days)
                meeting_name = ("%s : %s, %s") % (
                    holiday.holiday_status_id.calendar_name
                    or holiday.holiday_status_id.display_name,
                    holiday.employee_id.name or holiday.category_id.name,
                    unit,
                )
                meeting_values["name"] = meeting_name
        return meetings_values_for_user_id
