# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    main_product_category_id = fields.Many2one(
        comodel_name="product.category",
        string="Main Product Category",
        ondelete="restrict",
    )
