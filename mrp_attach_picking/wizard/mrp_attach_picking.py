# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MrpAttachPicking(models.TransientModel):
    _name = 'mrp.attach.picking'
    _description = 'Attach production order to picking'

    production_id = fields.Many2one(
        'mrp.production',
        'Production Order',
        required=True,
        readonly=True,
        domain=[]
    )
    product_id = fields.Many2one(
        related='production_id.product_id',
        string='Product',
        required=True,
        readonly=True,
    )
    product_uom_qty = fields.Float(related='production_id.product_uom_qty', )
    move_id = fields.Many2one(
        'stock.move',
        'Move',
        required=True,
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')

        if active_model == 'mrp.production' and active_id:
            production_id = self.env['mrp.production'].browse(active_id)
            # Assign wizard default values
            product_id = production_id.mapped('product_id')
            rec.update(
                {
                    'production_id': production_id.id,
                    'product_id': product_id.id,
                }
            )
        return rec

    def do_attach(self):
        self.ensure_one()
        if not self.move_id:
            raise ValidationError(_('A valid stock move must be selected.'))
        # Filter finished move in case of some of them are cancelled
        move_finished_ids = self.production_id.move_finished_ids.filtered(
            lambda x: x.state in ('confirmed', 'assigned', 'done')
        )
        if not move_finished_ids:
            raise ValidationError(
                _('None of the production finished moves can be linked.')
            )
        # In case of one move is already done, set the next
        # move state to assigned
        if 'done' in move_finished_ids.mapped('state'):
            state = 'assigned'
        else:
            state = 'waiting'
        # Link chosen move with our production order
        self.move_id.write(
            {
                'procure_method': 'make_to_order',
                'state': state,
                'move_orig_ids': [(6, 0, move_finished_ids.ids)],
            }
        )
