# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import api, fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    _order = 'production_id desc, sequence asc'

    # sequence = fields.Integer(
    #     'Sequence',
    #     oldname='openupgrade_legacy_10_0_sequence',
    # )
    # working_date = fields.Datetime(help="Date on which the work is done.")
