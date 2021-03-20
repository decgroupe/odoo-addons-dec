# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import api, fields, models


class SoftwareLicense(models.Model):
    _inherit = 'software.license'

    dongle_id = fields.Integer('Dongle ID')
    dongle_product_id = fields.Integer(
        related='application_id.dongle_product_id',
        string='Dongle Product ID',
    )

    classic = fields.Boolean('System Classic')
    cave = fields.Boolean('System Cave')
    rift = fields.Boolean('System Rift')
    vive = fields.Boolean('System Vive')

    @api.multi
    def _get_aeroo_report_filename(self):
        names = [x.serial or str(x.id) for x in self]
        res = '-'.join(names)
        return res
