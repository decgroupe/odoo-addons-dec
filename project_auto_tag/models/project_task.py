# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo import _, api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if self._need_auto_tag(vals):
            rec._auto_tag()
        return rec

    def write(self, vals):
        res = super().write(vals)
        if self._need_auto_tag(vals):
            for rec in self:
                rec._auto_tag()
        return res

    @api.model
    def _need_auto_tag(self, vals):
        """Check if the task created or edited should be linked to an existing tag
        based on their values.
        eg: if the task is linked to reference_id, then check for
        `vals.get('reference_id')`
        """
        return False

    def _get_auto_tag_data(self):
        """Return the tag that should be linked to this task.
        :return: tuple (origin, act_values)
            - origin: dict with keys 'res_id' and 'res_model' as the origin of the
            activity
            - tag_id: record of the tag to be linked to the task
        """
        self.ensure_one()
        origin = {
            "res_id": False,
            "res_model": False,
        }
        tag_id = False
        return origin, tag_id

    def _auto_tag(self):
        self.ensure_one()
        # avoid infinite loop
        if self.env.context.get("auto_tag_origin", False):
            return
        origin, tag_id = self._get_auto_tag_data()
        if tag_id:
            self.with_context(auto_tag_origin=origin).write(
                {"tag_ids": [(4, tag_id.id)]},
            )
