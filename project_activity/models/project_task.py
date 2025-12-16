# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo import _, models

from odoo.addons.project.models.project_task import CLOSED_STATES


class ProjectTask(models.Model):
    _inherit = "project.task"

    def create(self, vals):
        rec = super().create(vals)
        if self.env.context.get("auto_activity", False):
            if not rec.user_ids:
                rec.create_to_assign_activity()
            if not rec.date_deadline:
                rec.create_to_plan_activity()
        return rec

    def write(self, vals):
        # rely only on task state (stage.is_closed field has been removed)
        if vals.get("state") in CLOSED_STATES:
            self.activity_unlink(
                [
                    "project_activity.mail_activity_to_assign",
                    "project_activity.mail_activity_to_plan",
                ]
            )
        if vals.get("user_ids"):
            self.activity_feedback(["project_activity.mail_activity_to_assign"])
        if vals.get("date_deadline"):
            self.activity_feedback(["project_activity.mail_activity_to_plan"])
        return super().write(vals)

    def _create_activity(self, act_type_xmlid, note, **act_values):
        self.ensure_one()
        activity_id = self.with_context(
            mail_activity_noautofollow=True,
        ).activity_schedule(act_type_xmlid=act_type_xmlid, note=note, **act_values)
        return activity_id

    def create_to_assign_activity(self, **act_values):
        return self._create_activity(
            act_type_xmlid="project_activity.mail_activity_to_assign",
            note=_("🚨 Auto: This task must be assigned"),
            **act_values,
        )

    def create_to_plan_activity(self, **act_values):
        return self._create_activity(
            act_type_xmlid="project_activity.mail_activity_to_plan",
            note=_("🚨 Auto: This task must be planned"),
            **act_values,
        )
