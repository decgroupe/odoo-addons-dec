# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Nov 2020

from odoo import fields, models, api, _
from odoo.addons.queue_job.job import job

class ReplaceTuple(models.TransientModel):
    _name = 'replace.bom.tuple'
    _description = 'Tuple to store product to replace'

    owner_id = fields.Many2one(
        'replace.bom.components',
        string='Owner',
        required=True,
        ondelete='cascade'
    )
    previous_product_id = fields.Many2one(
        'product.product',
        string='Previous',
        required=True,
    )
    new_product_id = fields.Many2one(
        'product.product',
        string='New',
        required=True,
    )


class ReplaceBomComponents(models.TransientModel):
    _name = 'replace.bom.components'
    _description = 'Replace BoM Components'

    replacement_ids = fields.One2many(
        'replace.bom.tuple',
        'owner_id',
        string='Replacements',
    )
    bom_ids = fields.Many2many(
        'mrp.bom',
        string='Bill of Materials',
        readonly=True,
    )
    bom_product_ids = fields.Many2many(
        'product.product',
        string='Products',
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        if active_model == 'mrp.bom' and active_ids:
            bom_ids = self.env['mrp.bom'].browse(active_ids)
            rec.update(
                {
                    'bom_ids':
                        bom_ids.ids,
                    'bom_product_ids':
                        bom_ids.mapped('bom_line_ids').mapped('product_id').ids,
                }
            )
        return rec

    @api.multi
    def action_replace(self):
        self.with_delay()._do_replace()

    @job
    def _do_replace(self):
        previous_product_ids = self.replacement_ids.mapped(
            'previous_product_id'
        )
        for bom_id in self.bom_ids:
            values = {'lines': {}}
            for bom_line in bom_id.bom_line_ids.filtered(
                lambda x: x.product_id in previous_product_ids
            ):
                for replacement_id in self.replacement_ids:
                    if bom_line.product_id == replacement_id.previous_product_id:
                        values['lines'][bom_line] = {
                            'before': bom_line.product_id,
                            'after': replacement_id.new_product_id,
                        }
                        bom_line.product_id = replacement_id.new_product_id
                        break

            bom_id.message_post_with_view(
                'mrp_bom_replace_components.track_bom_line_template',
                values=values,
                subtype_id=self.env.ref('mail.mt_note').id
            )
