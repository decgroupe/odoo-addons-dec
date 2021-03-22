# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models


class SoftwareLicense(models.Model):
    _name = 'software.license'
    _description = 'License'
    _rec_name = 'serial'
    _order = 'id desc'

    active = fields.Boolean(
        'Active',
        default=True,
        help="If unchecked, it will allow you to hide the license "
        "without removing it.",
    )
    serial = fields.Char(required=True, )
    application_id = fields.Many2one(
        'software.license.application',
        'Application',
        required=True,
    )
    hardware_id = fields.Char(
        'Hardware ID',
        oldname='dongle_id_encrypted',
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        domain=[],
        change_default=True,
    )
    production_id = fields.Many2one('mrp.production', 'Production')
    partner_id = fields.Many2one('res.partner', 'Partner')
    datetime = fields.Datetime(
        'Modification Date',
        default=fields.Datetime.now,
    )
    info = fields.Text('Informations')
