# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sept 2020

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        return super().copy(default=default)
