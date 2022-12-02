# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, models, fields


class GitlabResource(models.Model):
    _name = 'gitlab.resource'
    _description = 'GitLab Resource'
    _rec_name = 'uid'

    type = fields.Selection(
        [
            ('user', 'User'),
            ('group', 'Group'),
            ('project', 'Project'),
        ],
        string='Type',
        required=True,
    )
    uid = fields.Integer(
        string='Backend ID',
        required=True,
        oldname="backend_id",
    )
    display_name = fields.Char(compute="_compute_display_name")

    _sql_constraints = [
        (
            'type_uid_uniq', 'unique(type, uid)',
            'Backend ID must be unique !'
        ),
    ]

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.display_name))
        return result

    @api.depends("type", "uid")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s ID: %d" % (rec.type, rec.uid)
