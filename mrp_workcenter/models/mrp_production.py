# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    assigned_workcenter_id = fields.Many2one(
        'mrp.workcenter',
        'Assigned to',
        required=False,
        oldname='assigned_workcenter',
    )
