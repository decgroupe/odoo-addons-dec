# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from Crypto.PublicKey import RSA
from odoo import api, fields, models


class SoftwareApplication(models.Model):
    _inherit = 'software.application'

    auto_generate_serial = fields.Boolean(
        string="Auto-generate Serial",
        help="Automatically generate a random pref-formatted serial when "
        "creating a new license for this application",
    )

    def write(self, vals):
        if vals.get('type') == 'other':
            vals.update({
                'auto_generate_serial': False,
            })
        return super().write(vals)
