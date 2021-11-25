# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import fields, models


class SoftwareLicensePass(models.Model):
    _inherit = 'software.license.pass'

    partner_zip_id = fields.Many2one(
        'res.city.zip',
        related='partner_id.zip_id',
        string="Partner's ZIP",
        store=True,
    )
    partner_city_id = fields.Many2one(
        'res.city',
        related='partner_id.city_id',
        string="Partner's City",
        store=True,
    )