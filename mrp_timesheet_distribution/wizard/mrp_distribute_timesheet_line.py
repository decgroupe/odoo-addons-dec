# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import fields, models


class MrpDistributeTimesheetLine(models.TransientModel):
    _name = "mrp.distribute.timesheet.line"
    _description = "Represents a sample of the distribution"

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
    )
    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Production",
    )
    start_time = fields.Datetime()
    end_time = fields.Datetime()

    def _prepare_analytic_line(self, name):
        diff = self.end_time - self.start_time
        hours = diff.total_seconds() / 3600
        vals = {
            "name": name,
            "project_id": self.project_id.id,
            "production_id": self.production_id.id,
            "date_time": self.start_time,
            "unit_amount": hours,
        }
        return vals
