# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import models, api, fields

SEARCH_SEPARATOR = ' →'


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
        if SEARCH_SEPARATOR in name:
            name = name.partition(SEARCH_SEPARATOR)[0]
        names = super(Project, self.with_context(
            name_search=True
        )).name_search(name=name, args=args, operator=operator, limit=limit)
        return names

    def name_get(self):
        if self.env.context.get('name_search'):
            return self.name_get_from_search()
        else:
            return super().name_get()

    @api.depends('name')
    def name_get_from_search(self):
        """ Custom naming with type to quickly identify a project
        """
        res = []
        for rec in self:
            name = rec.name
            identifications = rec._get_name_identifications()
            if identifications:
                name = '%s%s %s' % (
                    name, SEARCH_SEPARATOR, ' '.join(identifications)
                )
            res.append((rec.id, name))
        return res

    @api.depends('type_id', 'type_id.complete_name')
    def _get_name_identifications(self):
        res = []
        self.ensure_one()
        # Add type
        if self.type_id:
            res.append(self.type_id.complete_name)
        return res
