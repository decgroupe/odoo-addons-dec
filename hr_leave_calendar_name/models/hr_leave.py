# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import api, models, _


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    def _prepare_holidays_meeting_values(self):
        self.ensure_one()
        meeting_values = super()._prepare_holidays_meeting_values()

        if self.leave_type_request_unit == 'hour':
            unit = _("%.2f hour(s)") % (self.number_of_hours_display)
        else:
            unit = _("%.2f day(s)") % (self.number_of_days)

        meeting_name = ("%s : %s, %s") % (
            self.holiday_status_id.calendar_name or
            self.holiday_status_id.display_name,
            self.employee_id.name or self.category_id.name,
            unit,
        )

        meeting_values['name'] = meeting_name
        return meeting_values
