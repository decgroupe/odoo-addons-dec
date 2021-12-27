# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import api, models


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

    def _get_employee_leave_manager(self, employee_id):
        parent_id = employee_id.parent_id
        is_manager = parent_id.user_id.has_group(
            'hr_holidays_manager.group_hr_holidays_supermanager'
        )
        if parent_id:
            if is_manager:
                return parent_id
            else:
                return self._get_employee_leave_manager(parent_id)
        else:
            return self.env['hr.employee']

    @api.multi
    def _sync_employee_details(self):
        super()._sync_employee_details()
        for holiday in self:
            manager_id = self._get_employee_leave_manager(holiday.employee_id)
            if manager_id and manager_id != holiday.manager_id:
                holiday.manager_id = manager_id
