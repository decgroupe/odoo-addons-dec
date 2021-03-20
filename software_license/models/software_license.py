# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models


class SoftwareLicense(models.Model):
    _name = 'software.license'
    _description = 'License'
    _rec_name = 'serial'
    _order = 'id desc'

    serial = fields.Char(required=True, )
    application_id = fields.Many2one(
        'software.license.application',
        'Application',
        required=True,
    )
    dongle_id = fields.Integer('Dongle ID')
    dongle_product_id = fields.Integer(
        related='application_id.dongle_product_id',
        string='Dongle Product ID',
    )
    hardware_id = fields.Char(
        'Hardware ID',
        oldname='dongle_id_encrypted',
    )
    classic = fields.Boolean('System Classic')
    cave = fields.Boolean('System Cave')
    rift = fields.Boolean('System Rift')
    vive = fields.Boolean('System Vive')
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

    @api.multi
    def _get_aeroo_report_filename(self):
        names = [x.serial or str(x.id) for x in self]
        res = '-'.join(names)
        return res
