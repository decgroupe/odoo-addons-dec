# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2021

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    partner_department_id = fields.Many2one(
        comodel_name="res.country.department",
        related="partner_id.department_id",
        string="Partner's Department",
        store=True,
    )
    partner_state_id = fields.Many2one(
        comodel_name="res.country.state",
        related="partner_id.state_id",
        string="Partner's State",
        store=True,
    )
