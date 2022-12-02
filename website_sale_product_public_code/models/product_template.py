# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    website_public_code = fields.Char(compute='_compute_website_public_code')

    @api.depends('default_code', 'public_code')
    def _compute_website_public_code(self):
        for rec in self:
            if rec.public_code:
                rec.website_public_code = rec.public_code
            elif rec.default_code:
                rec.website_public_code = rec.default_code
            else:
                rec.website_public_code = False
