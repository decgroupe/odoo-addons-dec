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

    @api.multi
    def set_main_public_category(self, categ_id):
        for rec in self:
            if not rec.public_categ_ids:
                categ_ids = [categ_id]
            else:
                categ_ids = [categ_id] + [
                    public_categ_id.id
                    for public_categ_id in rec.public_categ_ids[1:]
                    if public_categ_id.id != categ_id
                ]
            rec.write({
                'public_categ_ids': [(6, 0, categ_ids)],
            })
