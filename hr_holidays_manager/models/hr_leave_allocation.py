# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import models


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    def _get_responsible_for_approval(self):
        """Override built-in method to use the same supermanager"""
        self.ensure_one()
        super()._get_responsible_for_approval()
        manager_id = self.env["hr.leave"]._get_employee_leave_manager(self.employee_id)
        return manager_id.user_id
