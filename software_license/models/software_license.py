# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _


class SoftwareLicense(models.Model):
    _name = 'software.license'
    _description = 'License'
    _rec_name = 'serial'
    _order = 'id desc'

    serial = fields.Char(
        size=64,
        required=True,
    )
    application_id = fields.Many2one(
        'licence.application',
        'Application',
        required=True,
    )
    dongle_id = fields.Integer('Dongle ID')
    dongle_product_id = fields.Integer('Dongle Product ID')
    dongle_id_encrypted = fields.Char(
        'Dongle ID Encrypted',
        size=64,
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
