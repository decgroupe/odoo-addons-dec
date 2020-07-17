# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import  fields, models


class SoftwareLicenseApplication(models.Model):
    _name = 'software.license.application'
    _description = 'License application'
    _order = 'application_id asc, name'

    application_id = fields.Integer(
        'AppID',
        required=True,
        default=0,
    )
    dongle_product_id = fields.Integer(
        'Dongle Product ID', help='Product ID to write into the dongle'
    )
    name = fields.Text(
        'Application',
        required=True,
    )
    info = fields.Text('Informations')
