# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models


class SoftwareApplication(models.Model):
    _inherit = 'software.application'

    dongle_product_id = fields.Integer(
        string='Dongle Product ID',
        help='Product ID to write into the dongle',
    )

    def write(self, vals):
        if 'type' in vals:
            if vals.get('type') == 'other':
                vals.update({
                    'dongle_product_id': 0,
                })
        return super().write(vals)
