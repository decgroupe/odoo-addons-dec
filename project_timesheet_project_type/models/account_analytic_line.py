# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import models, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    project_type_id = fields.Many2one(
        comodel_name='project.type',
        related='project_id.type_id',
        store=True,
    )
