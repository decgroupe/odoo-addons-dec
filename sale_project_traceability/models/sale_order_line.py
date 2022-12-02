# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    task_ids = fields.One2many(
        'project.task',
        'sale_line_id',
        string='Tasks',
    )
