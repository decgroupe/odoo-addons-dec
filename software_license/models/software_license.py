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
    serial = fields.Char(
        required=True,
        help="Unique serial used as an authorization identifier",
    )
    application_id = fields.Many2one(
        'software.license.application',
        'Application',
        required=True,
    )
    # Renamed to hardware_identifier, a computed field to get data from first
    # hardware_ids
    hardware_id = fields.Char(
        'Hardware ID',
        oldname='dongle_id_encrypted',
    )
    hardware_ids = fields.One2many(
        comodel_name='software.license.hardware',
        inverse_name='license_id',
        string="Hardware Identifiers",
        copy=False,
        help="Unique hardware identifiers sent by client application made to "
        "identify a system. This identifier must not change over time or "
        "activation related data would be invalidated"
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
