# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import api, fields, models


class MrpDistributeTimesheetReason(models.Model):
    _name = 'mrp.distribute.timesheet.reason'
    _order = "sequence, id"
    _description = 'Selectable reason used when distributing a timesheet'

    sequence = fields.Integer(
        'Sequence',
        default=1,
        help="Gives the sequence order when displaying.",
    )
    name = fields.Char(translate=True)
