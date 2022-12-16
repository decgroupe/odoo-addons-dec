# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import models, fields, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_line_warn = fields.Selection(
        selection_add=[(
            'block_confirm',
            'Block Confirmation Message',
        )],
        ondelete={'block_confirm': 'set default'},
    )
