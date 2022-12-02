# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    production_ids = fields.One2many(
        'mrp.production',
        'project_id',
        string="Productions",
    )
    production_count = fields.Integer(
        compute='_compute_production_count',
        string="Production Count",
        store=True,
    )
    label_productions = fields.Char(
        string='Use Productions as',
        default=lambda s: _('Productions'),
        translate=True,
        help="Gives label to productions on project's kanban view.",
    )
    todo_production_count = fields.Integer(
        string="To-do Production Count",
        compute='_compute_production_count',
        store=True,
    )

    @api.depends('production_ids', 'production_ids.state')
    def _compute_production_count(self):
        for record in self:
            record.production_count = len(record.production_ids)
            record.todo_production_count = len(
                record.production_ids.
                filtered(lambda p: p.state not in ('done', 'cancel'))
            )
