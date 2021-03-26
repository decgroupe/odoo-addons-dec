# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import api, fields, models


class SoftwareLicense(models.Model):
    _inherit = 'software.license'

    dongle_product_id = fields.Integer(
        related='application_id.dongle_product_id',
        string='Dongle Product ID',
        store=True,
    )

