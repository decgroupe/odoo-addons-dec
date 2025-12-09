# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _set_valuation_type(self):
        # Do not set property_valuation otherwise category valuation property
        # will never be taken into account
        pass
