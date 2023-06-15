# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    product_state_id = fields.Many2one(
        related="product_tmpl_id.product_state_id",
        readonly=False,
        store=True,
    )