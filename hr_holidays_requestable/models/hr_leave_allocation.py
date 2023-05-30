# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2022

from odoo import fields, models


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    holiday_status_id = fields.Many2one(
        domain=[
            "|",
            ("valid", "=", True),
            ("requestable_from_valid", "=", True),
        ],
    )

    # Copy from odoo/addons/hr_holidays/models/hr_leave_allocation.py
    def _default_holiday_status_id(self):
        super._default_holiday_status_id()
        if self.user_has_groups("hr_holidays.group_hr_holidays_user"):
            domain = [
                "|",
                ("valid", "=", True),
                ("requestable_from_valid", "=", True),
            ]
        else:
            domain = [
                "|",
                ("valid", "=", True),
                ("allocation_type", "in", ("no", "fixed_allocation")),
                ("requestable_from_valid", "=", True),
            ]
        return self.env["hr.leave.type"].search(domain, limit=1)
