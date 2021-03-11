# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project',
        copy=False,
    )
    task_id = fields.Many2one(
        string='Task',
        comodel_name='project.task',
        copy=False,
    )

    @api.onchange('project_id')
    def _onchange_project(self):
        self.task_id = False
