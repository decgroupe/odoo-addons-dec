# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    public_categ_id = fields.Many2one(
        'product.public.category',
        string='Website Main Product Category',
        compute='_compute_public_categ_id',
        store=True,
    )

    @api.multi
    @api.depends('public_categ_ids')
    def _compute_public_categ_id(self):
        for record in self:
            record.public_categ_id = record.public_categ_ids \
                and record.public_categ_ids[0] or False
