# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import fields, models, api


class Department(models.Model):
    _inherit = "hr.department"

    signature_logo_url = fields.Char(
        string='Logo URL',
        help="Logo used to replace the one used to render the user signature",
    )
    signature_primary_color = fields.Char(
        string='Primary Color',
        help="Color used to replace the one used to render the user signature",
    )
