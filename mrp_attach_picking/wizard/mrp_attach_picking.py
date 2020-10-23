# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, fields, models


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
    product_uom_qty = fields.Float(
        related='production_id.product_uom_qty',
    )
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

    # def onchange_move_id(self, cr, uid, ids, picking_id, move_id, context=None):
    #     if isinstance(ids, (int, long)):
    #         ids = [ids]
    #     if context is None:
    #         context = {}

    #     result = {}
    #     stock_move_obj = self.pool.get('stock.move')
    #     stock_picking_obj = self.pool.get('stock.picking')

    #     if move_id:
    #         move = stock_move_obj.browse(cr, uid, move_id, context=context)
    #         if move.picking_id and move.picking_id.id != picking_id:
    #             result = {'picking_id': move.picking_id.id}

    #     return {'value': result}

    def do_attach(self):
        pass

    # def do_attach(self, cr, uid, ids, context=None):
    #     if isinstance(ids, (int, long)):
    #         ids = [ids]
    #     if context is None:
    #         context = {}

    #     mrp_production_obj = self.pool.get('mrp.production')
    #     stock_move_obj = self.pool.get('stock.move')
    #     mrp_attach = self.browse(cr, uid, ids[0], context=context)
    #     if mrp_attach.production_id:
    #         mrp_production = mrp_production_obj.browse(cr, uid, mrp_attach.production_id.id, context=context)

    #         if mrp_attach.move_id:
    #             move_src_ids = stock_move_obj.search(cr, uid, [('move_dest_id', '=', mrp_attach.move_id.id)], context=context)

    #             if move_src_ids:
    #                 raise osv.except_osv(_('Error !'),_('This move is already assigned.'))

    #             if not mrp_production.move_prod_id and not move_src_ids:
    #                 data = {
    #                     'origin': ('%s:%s') % (mrp_production.origin or 'PROTO', mrp_attach.move_id.picking_id.origin),
    #                     'partner_id': mrp_attach.move_id.picking_id.partner_id.id,
    #                     'address_id': mrp_attach.move_id.picking_id.address_id.id,
    #                     'move_prod_id': mrp_attach.move_id.id,
    #                 }

    #                 mrp_production_obj.write(cr, uid, [mrp_production.id], data, context=context)

    #                 for move in mrp_production.move_created_ids:
    #                     stock_move_obj.write(cr, uid, [move.id], {'move_dest_id': mrp_attach.move_id.id}, context=context)
    #         else:
    #             raise osv.except_osv(_('Error !'),_('You must select a move.'))
    #     else:
    #         raise osv.except_osv(_('Error !'),_('You must select a production order.'))

    #     return {}