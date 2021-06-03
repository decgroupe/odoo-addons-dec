# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jun 2021

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    production_id = fields.Many2one(
        comodel_name='mrp.production',
        string="Production Order",
        copy=False,
    )
    bom_line_id = fields.Many2one(
        'mrp.bom.line',
        string="Line of the Bill of Material",
    )
    # To remove when manual reassigment is finished
    origin = fields.Char(string="Legacy Origin")
