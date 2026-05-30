# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import api, models


class Project(models.Model):
    _inherit = ["project.project", "mail.activity.schedule.mixin"]
    _name = "project.project"

    def _get_schedule_date_fields(self):
        """Map scheduling mixin date keys to project date fields."""
        res = super()._get_schedule_date_fields()
        res.update(
            {
                "start": "date_start",
                "stop": "date",
                "deadline": "date",
            }
        )
        return res

    @api.depends("active")
    def _compute_schedulable(self):
        """Recompute schedulable when project activation changes."""
        return super()._compute_schedulable()

    def _is_schedulable(self):
        """Allow scheduling only for active projects."""
        return super()._is_schedulable() and self.active
