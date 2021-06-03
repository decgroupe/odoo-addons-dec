# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import models, api, fields


class Project(models.Model):
    _inherit = "project.project"

    is_contract = fields.Boolean(
        string="Is for a contract",
        compute="_compute_from_type",
        store=True,
    )

    is_time_tracking = fields.Boolean(
        string="Is for time tracking",
        compute="_compute_from_type",
        store=True,
    )

    @api.multi
    @api.depends('type_id')
    def _compute_from_type(self):
        contract_type = self.env.ref('project_identification.contract_type')
        time_tracking_type = self.env.ref(
            'project_identification.time_tracking_type'
        )
        for rec in self:
            rec.is_contract = rec.type_id == contract_type
            rec.is_time_tracking = rec.type_id == time_tracking_type

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # Make a search with default criteria
        names = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        # Add type to quickly identify a project
        result = []
        for item in names:
            project = self.browse(item[0])[0]
            name = item[1]
            type_id = project.type_id
            if type_id:
                name = '%s / %s' % (type_id.complete_name, project.name)
            result.append((item[0], name))
        return result
