# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        for rec, vals in zip(record_ids, vals_list, strict=True):
            if self._need_auto_activity(vals):
                rec._auto_activity()
        return record_ids

    @api.model
    def _need_auto_activity(self, vals):
        """Check if the task created or edited also needs to create an automatic
        activity based on their values.
        eg: if the task is linked to reference_id, then check for
        `vals.get('reference_id')`
        """
        return False

    def _get_auto_activity_data(self):
        """Return the data to create automatic activities for the task.
        :return: tuple (origin, act_values)
            - origin: dict with keys 'res_id' and 'res_model' as the origin of the
            activity
            - act_values: dict with values that will be used to create the activity
        """
        self.ensure_one()
        origin = {
            "res_id": False,
            "res_model": False,
        }
        act_values = {}
        return origin, act_values

    def _auto_activity(self):
        self.ensure_one()
        # avoid infinite loop
        if self.env.context.get("auto_activity_origin", False):
            return
        origin, act_values = self._get_auto_activity_data()
        self.with_context(auto_activity_origin=origin).create_to_assign_activity(
            **act_values,
        )
        self.with_context(auto_activity_origin=origin).create_to_plan_activity(
            **act_values,
        )
