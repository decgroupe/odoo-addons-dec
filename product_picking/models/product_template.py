# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    picking_uom = fields.Selection(
        selection=[
            ("default_uom", "Default UoM"),
            ("purchase_uom", "Purchase UoM"),
        ],
        string="Picking UoM",
        default=False,
    )
