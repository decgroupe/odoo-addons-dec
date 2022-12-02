# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import models, api, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    project_identification = fields.Char(
        string="Project Identification",
        compute="_compute_project_identification",
    )

    @api.depends('project_id')
    def _compute_project_identification(self):
        for rec in self.filtered('project_id'):
            identifications = rec.project_id._get_name_identifications()
            rec.project_identification = ' / '.join(identifications)
