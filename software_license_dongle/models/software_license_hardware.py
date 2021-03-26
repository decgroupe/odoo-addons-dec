# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import api, fields, models


class SoftwareLicenseHardware(models.Model):
    _inherit = 'software.license.hardware'

    dongle_identifier = fields.Integer(
        string='Dongle ID',
        help="Unique device ID set and given by then dongle manufacturer",
    )
