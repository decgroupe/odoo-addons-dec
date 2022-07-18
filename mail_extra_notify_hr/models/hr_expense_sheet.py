# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from odoo import models, api, fields


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def _get_user_assigned_extra_values(self):
        self.ensure_one()
        res = {}

        if self.user_id:
            key, value = self._get_user_assigned_extra_field_value(
                self,
                'employee_id',
            )
            res[key] = value
        return res
