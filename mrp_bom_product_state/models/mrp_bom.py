# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    product_state = fields.Selection(
        related='product_tmpl_id.state',
        readonly=False,
        store=True,
        string='Product State',
    )
