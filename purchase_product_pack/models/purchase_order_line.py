# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    pack_type = fields.Selection(related='product_id.pack_type', )
    pack_component_price = fields.Selection(
        related='product_id.pack_component_price',
    )

    # Fields for common packs
    pack_depth = fields.Integer(
        'Depth', help='Depth of the product if it is part of a pack.'
    )
    pack_parent_line_id = fields.Many2one(
        'purchase.order.line',
        'Pack',
        help='The pack that contains this product.',
        ondelete="cascade",
    )
    pack_child_line_ids = fields.One2many(
        'purchase.order.line', 'pack_parent_line_id', 'Lines in pack'
    )
    pack_modifiable = fields.Boolean(help='The parent pack is modifiable')

    def expand_pack_line(self, write=False):
        self.ensure_one()
        # if we are using update_pricelist or checking out on ecommerce we
        # only want to update prices
        do_not_expand = self._context.get('update_prices') or \
            self._context.get('update_pricelist', False)
        if (self.product_id.pack_ok and self.pack_type == 'detailed'):
            for subline in self.product_id.get_pack_lines():
                vals = subline.get_purchase_order_line_vals(self, self.order_id)
                vals['sequence'] = self.sequence
                if write:
                    existing_subline = self.search(
                        [
                            ('product_id', '=', subline.product_id.id),
                            ('pack_parent_line_id', '=', self.id),
                        ],
                        limit=1
                    )
                    # if subline already exists we update, if not we create
                    if existing_subline:
                        if do_not_expand:
                            vals.pop('product_qty')
                        existing_subline.write(vals)
                    elif not do_not_expand:
                        self.create(vals)
                else:
                    self.create(vals)

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.expand_pack_line()
        return record

    def write(self, vals):
        res = super().write(vals)
        if 'product_id' in vals or 'product_qty' in vals:
            for record in self:
                record.expand_pack_line(write=True)
        return res

    def unlink(self):
        """Remove previously the pack children lines for avoiding issues in
        the cache.
        """
        children = self.mapped('pack_child_line_ids')
        if children:
            children._pre_unlink()
            children.unlink()
        return super().unlink()

    def _pre_unlink(self):
        """Delete existing moves before calling unlink (because some modules
        like 'purchase_stock_cancel'could already have unset the link with
        'move_dest_ids').
        """
        for record in self:
            if record.pack_parent_line_id and record.move_dest_ids:
                record.move_dest_ids._action_cancel()
                record.move_dest_ids.unlink()

    def _is_editable(self):
        #res = super().is_line_editable()
        res = True
        if self.pack_parent_line_id and not self.pack_modifiable:
            res = False
        return res

    @api.onchange(
        'product_id', 'product_qty', 'product_uom', 'price_unit', 'name',
        'taxes_id'
    )
    def check_pack_line_modify(self):
        """ Do not let to edit a purchase order line if this one belongs to pack
        """
        if not self._origin._is_editable():
            raise UserError(
                _(
                    'You can not change this line because is part of a pack'
                    ' included in this order'
                )
            )

    def action_open_parent_pack_product_view(self):
        domain = [
            (
                'id', 'in',
                self.mapped('pack_parent_line_id').mapped('product_id').ids
            )
        ]
        return {
            'name': _('Parent Product'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain
        }

    def _get_pack_line_move_data(self, move):
        self.ensure_one()
        res = {
            # Set from purchase line
            "product_id": self.product_id.id,
            "product_uom": self.product_id.uom_id.id,
            "product_uom_qty": self.product_uom_qty,
            "name": self.name,
            "created_purchase_line_id": self.id,
            # Copy parent move data
            "company_id": move.company_id.id,
            "picking_id": move.picking_id.id,
            "picking_type_id": move.picking_type_id.id,
            "reference": move.reference,
            "date": move.date,
            "date_deadline": move.date_deadline,
            "propagate": move.propagate,
            "partner_id": move.partner_id.id,
            "procure_method": move.procure_method,
            "location_id": move.location_id.id,
            "location_dest_id": move.location_dest_id.id,
            "origin": move.origin,
            "group_id": move.group_id.id,
            "warehouse_id": move.warehouse_id.id,
            "raw_material_production_id": move.raw_material_production_id.id,
            "auto_validate": move.auto_validate,
            "move_dest_ids": [(6, 0, move.move_dest_ids.ids)],
            "state": move.state,
            "sequence": move.sequence,
            # Set as pack line, will auto-set pack_child_move_ids on its parent
            "pack_parent_move_id": move.id,
        }
        return res

    def _create_pack_stock_moves(self):
        moves = self.env['stock.move']
        for line in self:
            if line.pack_parent_line_id and line.pack_parent_line_id.move_dest_ids:
                parent_move = line.pack_parent_line_id.move_dest_ids[0]
                data = line._get_pack_line_move_data(parent_move)
                child_move = self.env['stock.move'].create(data)
                moves += child_move
        return moves

    def _get_parent_pack_stock_moves(self):
        moves = self.env['stock.move']
        for line in self:
            # Set parent pack move done since there is no
            # physical pack item to receive
            if line.pack_child_line_ids:
                moves += line.move_dest_ids
                moves += line.move_ids
        return moves
