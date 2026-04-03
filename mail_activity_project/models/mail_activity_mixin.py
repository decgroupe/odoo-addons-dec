# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo import api, models


class MailActivityMixin(models.AbstractModel):
    _inherit = "mail.activity.mixin"

    @api.model_create_multi
    def create(self, vals_list):
        """Create records and update activity projects when a project field is set."""
        recs = super().create(vals_list)
        for rec, vals in zip(recs, vals_list, strict=True):
            if self._activity_project_need_update(vals):
                rec._update_activity_project()
        return recs

    def write(self, vals):
        """Write record values and refresh activity project links when needed."""
        res = super().write(vals)
        if res and self._activity_project_need_update(vals):
            self._update_activity_project()
        return res

    @api.model
    def _get_project_field_name(self):
        """Return the name of the field holding the project on this model."""
        return "project_id"

    @api.model
    def _activity_project_need_update(self, vals):
        """Return True if activity projects must be refreshed given the changed vals."""
        res = False
        project_field_name = self._get_project_field_name()
        if project_field_name in self._fields:
            # use set intersection to find out if the project field of
            # linked activities must be updated
            depends_fields = [project_field_name]
            if depends_fields and (set(vals) & set(depends_fields)):
                res = True
        return res

    def _update_activity_project(self):
        """Propagate the project value of each record to all its linked activities."""
        project_field_name = self._get_project_field_name()
        for rec in self:
            project_id = rec[project_field_name]
            rec.activity_ids.write({"project_id": project_id.id})
