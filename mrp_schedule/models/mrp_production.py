# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = ["mrp.production", "mail.activity.schedule.mixin"]
    _name = "mrp.production"

    def _get_schedule_date_fields(self):
        """Map manufacturing dates used by scheduling activities."""
        res = super()._get_schedule_date_fields()
        res.update(
            {
                "start": "date_planned_start",
                "stop": "date_planned_finished",
                "deadline": "date_planned_finished",
            }
        )
        return res

    @api.depends("state")
    def _compute_schedulable(self):
        """Recompute schedulable when state changes on manufacturing orders."""
        return super()._compute_schedulable()

    def _is_schedulable(self):
        """Allow scheduling only for non-completed and non-cancelled orders."""
        return super()._is_schedulable() and self.state not in ["done", "cancel"]
