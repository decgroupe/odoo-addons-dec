# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    loc_rack = fields.Char("Rack", size=16)
    loc_row = fields.Char("Row", size=16)
    loc_case = fields.Char("Case", size=16)
