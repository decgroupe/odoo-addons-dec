# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    main_product_category_id = fields.Many2one(
        comodel_name="product.category",
        string="Main Product Category",
        related="company_id.main_product_category_id",
        readonly=False,
    )
