# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo import api, models


class MailActivityMixin(models.AbstractModel):
    _inherit = "mail.activity.mixin"

    @api.model
    def create(self, vals):
        rec = super(MailActivityMixin, self).create(vals)
        if rec and self._activity_project_need_update(vals):
            rec._update_activity_project()
        return rec

    def write(self, vals):
        res = super().write(vals)
        if res and self._activity_project_need_update(vals):
            self._update_activity_project()
        return res

    @api.model
    def _get_project_field_name(self):
        return "project_id"

    @api.model
    def _activity_project_need_update(self, vals):
        res = False
        project_field_name = self._get_project_field_name()
        if project_field_name in self._fields:
            # Use set intersection to find out if the `partner_id` of
            # linked activities must be updated
            depends_fields = [project_field_name]
            if depends_fields and (set(vals) & set(depends_fields)):
                res = True
        return res

    def _update_activity_project(self):
        project_field_name = self._get_project_field_name()
        for rec in self:
            project_id = rec[project_field_name]
            rec.activity_ids.write({"project_id": project_id.id})
