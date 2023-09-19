# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import models


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    def _get_employee_leave_manager(self, employee_id):
        """Recursive function to get the nearest parent (hierachically) with
        super-manager rights.
        """
        parent_id = employee_id.parent_id
        is_manager = parent_id.user_id.has_group(
            "hr_holidays_manager.group_hr_holidays_supermanager"
        )
        if parent_id:
            if is_manager:
                return parent_id
            else:
                return self._get_employee_leave_manager(parent_id)
        else:
            return self.env["hr.employee"]

    def _compute_from_employee_id(self):
        super()._compute_from_employee_id()
        for holiday in self:
            manager_id = self._get_employee_leave_manager(holiday.employee_id)
            if manager_id and manager_id != holiday.manager_id:
                holiday.manager_id = manager_id

    def _get_responsible_for_approval(self):
        responsible = super()._get_responsible_for_approval()
        if responsible == self.env.user:
            manager = self._get_employee_leave_manager(self.employee_id)
            if manager:
                responsible = manager.user_id
        return responsible
