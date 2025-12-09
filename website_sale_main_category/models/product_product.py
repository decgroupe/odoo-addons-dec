# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2022

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def set_main_public_category(self, categ_id):
        self.mapped("product_tmpl_id").set_main_public_category(categ_id)
