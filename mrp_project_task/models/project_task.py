# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Production Order",
        copy=False,
    )
    bom_line_id = fields.Many2one(
        comodel_name="mrp.bom.line",
        string="Line of the Bill of Material",
    )

    def _get_name_identifications(self, base_name=None):
        res = super()._get_name_identifications(base_name)
        # Add production to quickly identify a task
        production_id = self.production_id
        if production_id:
            production_name = f"🔧 {production_id.name}"
            res.append(production_name)
        return res
