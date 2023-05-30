# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.onchange("project_id")
    def _onchange_project_id(self):
        res = super()._onchange_project_id()
        # Force domain reset to allow selection of any task because OCA module
        # `hr_timesheet_task_domain` does not allow selecting closed tasks
        if "domain" in res and "task_id" in res["domain"]:
            if self.project_id:
                res["domain"]["task_id"] = [
                    ("project_id", "=", self.project_id.id),
                ]
            else:
                res["domain"]["task_id"] = []
        return res
