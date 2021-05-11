# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    partner_department_id = fields.Many2one(
        'res.country.department',
        related='partner_id.department_id',
        string="Department",
        store=True,
    )
    partner_state_id = fields.Many2one(
        'res.country.state',
        related='partner_id.state_id',
        string="State",
        store=True,
    )
