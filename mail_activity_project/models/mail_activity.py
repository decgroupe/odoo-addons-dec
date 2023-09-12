# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2022

import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"

    project_id = fields.Many2one(
        comodel_name="project.project",
        index=True,
        compute="_compute_project_id",
        store=True,
    )

    @api.depends("res_model", "res_id")
    def _compute_project_id(self):
        for activity in self:
            res_model = activity.res_model
            res_id = activity.res_id
            activity.project_id = False
            if not res_model or not res_id:
                _logger.error(
                    "Activity %d is missing a model/id " "(res_model=%s, res_id=%d)",
                    activity.id,
                    res_model,
                    res_id,
                )
                continue
            if res_model == "project.project":
                activity.project_id = res_id
            else:
                res_model_id = activity.env[res_model].search([("id", "=", res_id)])
                # Check for existing function as this case could happen when
                # compute is called from a hook (post_install)
                if hasattr(self, "_get_project_field_name"):
                    project_field_name = res_model_id._get_project_field_name()
                else:
                    project_field_name = "project_id"
                if project_field_name in res_model_id._fields:
                    project_id = res_model_id[project_field_name]
                    activity.project_id = project_id
                else:
                    activity.project_id = None
