# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Defined in `odoo/addons/hr_expense/models/product_template.py`
    can_be_expensed = fields.Boolean(index=True)
