# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models


class SoftwareLicenseApplication(models.Model):
    _inherit = 'software.license.application'

    dongle_product_id = fields.Integer(
        string='Dongle Product ID',
        help='Product ID to write into the dongle',
    )
