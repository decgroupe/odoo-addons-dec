# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import fields, models


class SoftwareApplicationImage(models.Model):
    _name = 'software.application.image'
    _description = 'Software Application Image'

    name = fields.Char('Name')
    image = fields.Binary('Image', attachment=True)
    application_id = fields.Many2one(
        'software.license.application',
        'Related Application',
        copy=True,
    )
