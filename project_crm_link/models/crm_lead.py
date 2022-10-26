# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2022

from odoo import api, models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"

    related_project_ids = fields.One2many(
        comodel_name='project.project',
        inverse_name='linked_lead_id',
        string='Related Projects',
    )

    related_project_count = fields.Integer(
        compute='_compute_related_project_count',
        string="Related Project Count",
    )

    @api.multi
    def action_view_related_projects(self):
        action = self.mapped('related_project_ids').action_view()
        if "context" not in action:
            action["context"] = {
                "group_by": "linked_lead_id",
                "bypass_supermanager_check": True,
            }
        return action

    def _compute_related_project_count(self):
        for rec in self:
            rec.related_project_count = len(rec.related_project_ids)
