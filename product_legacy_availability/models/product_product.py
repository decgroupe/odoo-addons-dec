# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Nov 2020

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, float_round, float_is_zero


class Product(models.Model):
    _inherit = 'product.product'

    legacy_qty_available = fields.Float(
        compute='_compute_product_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Quantity On Hand (legacy)',
        help="Current quantity of products.\n"
        "In a context with a single Stock Location, this includes "
        "goods stored at this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods stored in the Stock Location of this Warehouse, or any "
        "of its children.\n"
        "In a context with a single Shop, this includes goods "
        "stored in the Stock Location of the Warehouse of this Shop, "
        "or any of its children.\n"
        "Otherwise, this includes goods stored in any Stock Location "
        "typed as 'internal'."
    )

    legacy_virtual_available = fields.Float(
        compute='_compute_product_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Quantity Available (legacy)',
        help="Forecast quantity (computed as Quantity On Hand "
        "- Outgoing + Incoming)\n"
        "In a context with a single Stock Location, this includes "
        "goods stored at this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods stored in the Stock Location of this Warehouse, or any "
        "of its children.\n"
        "In a context with a single Shop, this includes goods "
        "stored in the Stock Location of the Warehouse of this Shop, "
        "or any of its children.\n"
        "Otherwise, this includes goods stored in any Stock Location "
        "typed as 'internal'."
    )

    legacy_incoming_qty = fields.Float(
        compute='_compute_product_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Incoming (legacy)',
        help="Quantity of products that are planned to arrive.\n"
        "In a context with a single Stock Location, this includes "
        "goods arriving to this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods arriving to the Stock Location of this Warehouse, or "
        "any of its children.\n"
        "In a context with a single Shop, this includes goods "
        "arriving to the Stock Location of the Warehouse of this "
        "Shop, or any of its children.\n"
        "Otherwise, this includes goods arriving to any Stock "
        "Location typed as 'internal'."
    )

    legacy_outgoing_qty = fields.Float(
        compute='_compute_product_available',
        digits=dp.get_precision('Product Unit of Measure'),
        string='Outgoing (legacy)',
        help="Quantity of products that are planned to leave.\n"
        "In a context with a single Stock Location, this includes "
        "goods leaving from this Location, or any of its children.\n"
        "In a context with a single Warehouse, this includes "
        "goods leaving from the Stock Location of this Warehouse, or "
        "any of its children.\n"
        "In a context with a single Shop, this includes goods "
        "leaving from the Stock Location of the Warehouse of this "
        "Shop, or any of its children.\n"
        "Otherwise, this includes goods leaving from any Stock "
        "Location typed as 'internal'."
    )

    def _compute_product_available(self):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """
        res = {}
        for rec in self:
            # qty_available
            c = self.env.context.copy()
            c.update({'states': ('done', ), 'what': ('in', 'out')})
            rec.legacy_qty_available = self.with_context(c) \
                .get_product_available().get(rec.id, 0.0)

            # virtual_available
            c = self.env.context.copy()
            c.update(
                {
                    'states': ('confirmed', 'waiting', 'assigned', 'done'),
                    'what': ('in', 'out')
                }
            )
            rec.legacy_virtual_available = self.with_context(c) \
                .get_product_available().get(rec.id, 0.0)

            # outgoing_qty
            c = self.env.context.copy()
            c.update(
                {
                    'states': ('confirmed', 'waiting', 'assigned'),
                    'what': ('out', )
                }
            )
            rec.legacy_outgoing_qty = self.with_context(c) \
                .get_product_available().get(rec.id, 0.0)

            # incoming_qty
            c = self.env.context.copy()
            c.update(
                {
                    'states': ('confirmed', 'waiting', 'assigned'),
                    'what': ('in', )
                }
            )
            rec.incoming_qty = self.with_context(c) \
                .get_product_available().get(rec.id, 0.0)

        return res

    def get_product_available(self):
        """ Finds whether product is available or not in particular warehouse.
        @return: Dictionary of values
        """

        location_obj = self.env['stock.location']
        warehouse_obj = self.env['stock.warehouse']
        # shop_obj = self.env['sale.shop']

        c = self.env.context
        states = c.get('states', [])
        what = c.get('what', ())
        if not self:
            self = self.search([])
            c = self.env.context
        res = {}.fromkeys(self.ids, 0.0)
        if not self.ids:
            return res

        if c.get('warehouse', False):
            lot_id = warehouse_obj.read(int(c['warehouse']),
                                        ['lot_stock_id'])['lot_stock_id'][0]
            if lot_id:
                c['location'] = lot_id

        if c.get('location', False):
            if type(c['location']) == type(1):
                location_ids = [c['location']]
            elif type(c['location']) in (type(''), type(u'')):
                location_ids = location_obj.search(
                    [('name', 'ilike', c['location'])]
                )
            else:
                location_ids = c['location']
        else:
            location_ids = []
            wids = warehouse_obj.with_context(c).search([])
            for w in wids:
                location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        if c.get('compute_child', True):
            child_location_ids = location_obj.search(
                [('location_id', 'child_of', location_ids)]
            )
            location_ids = child_location_ids or location_ids

        uom_ids = []
        # this will be a dictionary of the product UoM by product id
        product2uom = {}
        for product in self.read(['uom_id']):
            product2uom[product['id']] = product['uom_id'][0]
            if not product['uom_id'][0] in uom_ids:
                uom_ids.append(product['uom_id'][0])

        # this will be a dictionary of the UoM resources we need for conversion purposes, by UoM id
        uoms_o = {}
        for uom in self.env['uom.uom'].with_context(c).browse(uom_ids):
            uoms_o[uom.id] = uom

        results = []
        results2 = []

        from_date = c.get('from_date', False)
        to_date = c.get('to_date', False)
        date_str = False
        date_values = False
        where = [
            tuple(location_ids.ids),
            tuple(location_ids.ids),
            tuple(self.ids),
            tuple(states)
        ]
        if from_date and to_date:
            date_str = "date>=%s and date<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
        elif from_date:
            date_str = "date>=%s"
            date_values = [from_date]
        elif to_date:
            date_str = "date<=%s"
            date_values = [to_date]
        if date_values:
            where.append(tuple(date_values))

        # TODO: perhaps merge in one query.
        if 'in' in what:
            # all moves from a location out of the set to a location in the set
            self._cr.execute(
                'select sum(product_uom_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id NOT IN %s '\
                'and location_dest_id IN %s '\
                'and product_id IN %s '\
                'and state IN %s ' + (date_str and 'and '+ date_str +' ' or '') +' '\
                'group by product_id,product_uom', tuple(where))
            results = self._cr.fetchall()
        if 'out' in what:
            # all moves from a location in the set to a location out of the set
            self._cr.execute(
                'select sum(product_uom_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id IN %s '\
                'and location_dest_id NOT IN %s '\
                'and product_id  IN %s '\
                'and state in %s ' + (date_str and 'and '+ date_str +' ' or '') + ' '\
                'group by product_id,product_uom', tuple(where))
            results2 = self._cr.fetchall()

        # Get the missing UoM resources
        uom_obj = self.env['uom.uom']
        uoms = list(map(lambda x: x[2], results)) \
            + list(map(lambda x: x[2], results2))
        if c.get('uom', False):
            uoms += [c['uom']]
        uoms = filter(lambda x: x not in uoms_o.keys(), uoms)
        if uoms:
            uoms = uom_obj.with_context(c).browse(list(set(uoms)))
            for o in uoms:
                uoms_o[o.id] = o

        # Count the incoming quantities
        for amount, prod_id, prod_uom in results:
            prod_uom_id = uoms_o[prod_uom]
            to_uom_id = uoms_o[c.get('uom', False) or product2uom[prod_id]]
            amount = prod_uom_id._compute_quantity(amount, to_uom_id)
            res[prod_id] += amount
        # Count the outgoing quantities
        for amount, prod_id, prod_uom in results2:
            prod_uom_id = uoms_o[prod_uom]
            to_uom_id = uoms_o[c.get('uom', False) or product2uom[prod_id]]
            amount = prod_uom_id._compute_quantity(amount, to_uom_id)
            res[prod_id] -= amount
        return res

    @api.multi
    def action_update_stock_quant_availability(self):
        Quant = self.env['stock.quant']
        if self.env.context.get('location', False):
            location_ids = self.env['stock.location'].browse(
                self.env.context['location']
            )
        else:
            location_ids = self.env.ref('stock.stock_location_stock')
        for rec in self:
            pr = rec.uom_id.rounding
            for location_id in location_ids:
                r = rec.with_context(location=[location_id.id])
                if not float_is_zero(r.qty_available, precision_rounding=pr):
                    Quant._update_available_quantity(
                        rec, location_id,
                        r.legacy_qty_available - r.qty_available
                    )
        Quant._merge_quants()
        Quant._unlink_zero_quants()
