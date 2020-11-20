# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Nov 2020

from odoo import fields, models, api, _
from odoo.exceptions import UserError


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

    # @api.onchange('order_id')
    # def _onchange_order_id(self):
    #     self.group_id = self.order_id.group_id

    # def _try_merging(self, line):
    #     match_line = False
    #     if self.order_id.order_line:
    #         for po_line in self.order_id.order_line:
    #             if line.product_id == po_line.product_id \
    #             and line.product_uom == po_line.product_uom \
    #             and line.price_unit == po_line.price_unit \
    #             and line.procurement_group_id == po_line.procurement_group_id \
    #             and line.taxes_id == po_line.taxes_id \
    #             and line.name == po_line.name:
    #                 match_line = po_line
    #                 break
    #     if match_line:
    #         match_line.product_qty += line.product_qty
    #         match_line.move_ids += line.move_ids
    #         match_line.move_dest_ids += line.move_dest_ids
    #         return True
    #     else:
    #         return False

    # def _pre_process_create(self):
    #     self.order_id = self.env['purchase.order'].with_context(
    #         {
    #             'trigger_onchange': True,
    #             'onchange_fields_to_trigger': [self.partner_id]
    #         }
    #     ).create({
    #         'partner_id': self.partner_id.id,
    #     })
    #     self._pre_process_merge()

    # def _pre_process_merge(self):
    #     # Remove selected order from list
    #     self.origin_order_ids -= self.order_id
    #     sequences = self.order_id.order_line.mapped('sequence')
    #     if sequences:
    #         sequence = max(sequences)
    #     else:
    #         sequence = 0
    #     for order in self.origin_order_ids:
    #         for line in order.order_line:
    #             if self.merge_quantities:
    #                 merged = self._try_merging(line)
    #                 line.unlink()
    #             else:
    #                 merged = False
    #             if not merged:
    #                 sequence += 1
    #                 line.write(
    #                     {
    #                         'sequence': sequence,
    #                         'order_id': self.order_id.id,
    #                     }
    #                 )
    #     self._set_origin()
    #     self.order_id.message_post_with_view(
    #         'purchase_merge.merged_with_template',
    #         values={
    #             'order_ids': self.origin_order_ids,
    #         },
    #         subtype_id=self.env.ref('mail.mt_note').id,
    #     )

    # def _set_origin(self):
    #     if self.order_id.origin:
    #         self.order_id.origin += ','
    #     else:
    #         self.order_id.origin = ''
    #     display_names = list(set(self.origin_order_ids.mapped('display_name')))
    #     self.order_id.origin += ','.join(display_names)

    # def _post_process_cancel(self):
    #     for order_id in self.origin_order_ids:
    #         order_id.message_post_with_view(
    #             'purchase_merge.merged_to_template',
    #             values={
    #                 'order_id': self.order_id,
    #             },
    #             subtype_id=self.env.ref('mail.mt_note').id,
    #         )
    #         order_id.button_cancel()

    # def _post_process_delete(self):
    #     self.post_process_cancel()
    #     for order_id in self.origin_order_ids:
    #         order_id.sudo().unlink()

    @api.multi
    def action_replace(self):
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

    # @api.multi
    # def action_merge(self):
    #     if self.pre_process == 'create':
    #         self._pre_process_create()
    #     elif self.pre_process == 'merge':
    #         self._pre_process_merge()

    #     if self.post_process == 'cancel':
    #         self._post_process_cancel()
    #     elif self.post_process == 'delete':
    #         self._post_process_delete()

    #     action_vals = {
    #         'name': _('Purchase Orders (after merge)'),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_id': self.order_id.id,
    #         'res_model': 'purchase.order',
    #         'view_id': False,
    #         'type': 'ir.actions.act_window',
    #     }
    #     return action_vals
