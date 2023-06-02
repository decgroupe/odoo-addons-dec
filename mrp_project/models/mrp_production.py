# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    project_id = fields.Many2one(
        string="Project",
        comodel_name="project.project",
        copy=False,
    )
