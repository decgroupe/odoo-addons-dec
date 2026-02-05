# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2022

from odoo import api, fields, models
from odoo.osv import expression


class Project(models.Model):
    _inherit = "project.project"

    # invert relation to get all opportunities from a project, note that the
    # `project_id` field on `crm.lead` model is defined by `crm_timesheet` OCA module
    opportunity_ids = fields.One2many(
        comodel_name="crm.lead",
        inverse_name="project_id",
        string="Opportunities",
        help="The same project can be used to store timesheets of "
        "multiple opportunities",
    )
    linked_lead_id = fields.Many2one(
        comodel_name="crm.lead",
        string="Opportunity Link",
        domain=[("type", "=", "opportunity")],
        help="Use this field to link this project with an existing opportunity. This "
        "will allow you to retrieve this project from the opportunity's form "
        "« Related Projects » tab.",
    )

    def _get_typefast_domain(self, name, operator):
        domain = super()._get_typefast_domain(name, operator)
        domain = expression.OR(
            # use `search_name` field from `crm_lead_number` module
            [domain, [("linked_lead_id.search_name", "ilike", name)]]
        )
        return domain

    @api.depends("linked_lead_id", "linked_lead_id.complete_name")
    def _get_name_identifications(self, base_name=None):
        res = super()._get_name_identifications(base_name=base_name)
        # Add opportunity lead
        if self.linked_lead_id:
            res.append(self.linked_lead_id.complete_name)
        return res
