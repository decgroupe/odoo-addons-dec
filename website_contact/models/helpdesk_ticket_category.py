# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import fields, models


class HelpdeskCategory(models.Model):
    _inherit = 'helpdesk.ticket.category'
    _order = 'sequence, name'

    sequence = fields.Integer(
        required=True,
        default=10,
        help="The sequence field is used to define order in which categories "
        "are displayed.",
    )
    public_ok = fields.Boolean(
        string="Public",
        help="Selectable on the public contact form",
        default=True,
    )
