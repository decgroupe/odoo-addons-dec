# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Nov 2020

from inspect import getargvalues
from odoo import fields, models, api
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_compare

TRACKED_FIELDS = [
    'product_id',
    'partner_id',
    'buy_consumable',
    'landmark',
    'product_qty',
    'product_uom_id',
    'public_price',
    'unit_price',
    'cost_price',
]


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def get_track_state(self):
        self.ensure_one()
        res = {}
        for line in self.bom_line_ids:
            read = line.read(fields=TRACKED_FIELDS)[0]
            vals = line._convert_to_write(read)
            res[line.id] = vals
        return res

    def set_track_state(self, previous_state):
        BomLine = self.env['mrp.bom.line']
        IrTranslation = self.env['ir.translation']
        # Convert previous state dict key to integer since XML-RPC
        # does not allow anything else than a string for a key
        rpc_previous_state = previous_state.copy()
        previous_state = {}
        for key in rpc_previous_state:
            previous_state[int(key)] = rpc_previous_state[key]

        values = {
            'tracked_fields': {},
            'edited_lines': {},
            'added_lines': {},
            'removed_lines': {},
        }
        for key in TRACKED_FIELDS:
            values['tracked_fields'][key] = \
                IrTranslation.get_field_string(BomLine._name)[key]

        current_state = self.get_track_state()
        add_ids = list(set(current_state) - set(previous_state))
        rem_ids = list(set(previous_state) - set(current_state))
        for id in current_state:
            if id not in add_ids and id not in rem_ids:
                previous_line_state = previous_state[id]
                current_line_state = current_state[id]
                diffkeys = []
                for k in current_line_state:
                    if current_line_state[k] != previous_line_state[k]:
                        # Specific case for floats, use float_compare to
                        # avoid detecting changes due to rounding issues
                        if isinstance(current_line_state[k], float):
                            digits = BomLine._fields[k].digits
                            if float_compare(
                                current_line_state[k],
                                previous_line_state[k],
                                precision_digits=digits[1]
                            ):
                                diffkeys.append(k)
                        else:
                            diffkeys.append(k)

                field_names = {}
                for key in diffkeys:
                    field_names[key] = IrTranslation.get_field_string(
                        BomLine._name
                    )[key]

                if diffkeys:
                    values['edited_lines'][id] = {
                        'line': self.env['mrp.bom.line'].browse(id),
                        'diffkeys': diffkeys,
                        'field_names': field_names,
                        'current': current_line_state,
                        'previous': previous_line_state,
                    }

        tracked_field_names = {}
        for key in TRACKED_FIELDS:
            tracked_field_names[key] = IrTranslation.get_field_string(
                BomLine._name
            )[key]

        for id in add_ids:
            current_line_state = current_state[id]
            line = self.env['mrp.bom.line'].browse(id)
            record_fields = {}
            for field in TRACKED_FIELDS:
                record_fields[field] = getattr(line, field)
            values['added_lines'][id] = {
                'line': line,
                'tracked_fields': TRACKED_FIELDS,
                'field_names': tracked_field_names,
                'record_fields': record_fields,
                'current': current_line_state,
            }

        for id in rem_ids:
            previous_line_state = previous_state[id]
            # Resolve IDs
            previous_line_state['product_id'] = self.env[
                'product.product'].browse(
                    previous_line_state['product_id']
                ).display_name
            previous_line_state['partner_id'] = self.env['res.partner'].browse(
                previous_line_state['partner_id']
            ).display_name
            previous_line_state['product_uom_id'] = self.env['uom.uom'].browse(
                previous_line_state['product_uom_id']
            ).display_name
            values['removed_lines'][id] = previous_line_state

        self.message_post_with_view(
            'mrp_bom_replace_components.track_bom_template',
            values=values,
            subtype_id=self.env.ref('mail.mt_note').id
        )
        return True
