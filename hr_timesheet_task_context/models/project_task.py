# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

from odoo import models, api, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.multi
    def _update_timesheet_project(self, project_id):
        self.ensure_one()
        self.timesheet_ids.write({
            'project_id': project_id
        })

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals and 'project_id' in vals:
            for rec in self:
                rec._update_timesheet_project(vals.get('project_id'))
        return res
