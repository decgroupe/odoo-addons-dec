# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class SoftwareAccountSupplier(models.Model):
    _name = 'software.account.supplier'
    _description = 'Software Account supplier'
    _order = 'id desc'

    name = fields.Text('Name', required=True)
    image = fields.Binary('Image')
    rules = fields.Text('Rules')
