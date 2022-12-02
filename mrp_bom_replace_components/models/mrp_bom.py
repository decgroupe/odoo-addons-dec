# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from inspect import getargvalues
from odoo import fields, models, api
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


def fix(res):
    """ 
        Ensure all dictionaries keys are string
        Ensure all tuples becomes lists
    """
    if res is None:
        return False
    elif type(res) == dict:
        return dict((str(key), fix(value)) for key, value in res.items())
    elif type(res) == list:
        return list(fix(x) for x in res)
    elif type(res) == tuple:
        return list(fix(x) for x in res)
    else:
        return res


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def write(self, vals):
        states = {}
        if 'bom_line_ids' in vals:
            for rec in self:
                states[rec.id] = rec.get_track_state()
        super().write(vals)
        if 'bom_line_ids' in vals:
            for rec in self:
                if rec.id in states:
                    rec.set_track_state(states[rec.id])

    def get_track_state(self):
        self.ensure_one()
        vals = self.bom_line_ids.read(fields=TRACKED_FIELDS)
        res = {}
        for v in vals:
            id = v.pop('id')
            res[id] = v
        res = fix(res)
        return res

    def set_track_state(self, previous_state):
        self.ensure_one()
        BomLine = self.env['mrp.bom.line']
        IrTranslation = self.env['ir.translation']

        edited_lines = {}
        added_lines = {}
        removed_lines = {}

        current_state = self.get_track_state()
        add_ids = list(set(current_state) - set(previous_state))
        rem_ids = list(set(previous_state) - set(current_state))
        for id in current_state:
            if id not in add_ids and id not in rem_ids:
                previous_line_state = previous_state[id]
                current_line_state = current_state[id]
                edited_fields = []
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
                                edited_fields.append(k)
                        else:
                            edited_fields.append(k)

                if edited_fields:
                    edited_lines[id] = {
                        'line': self.env['mrp.bom.line'].browse(int(id)),
                        'edited_fields': edited_fields,
                        'current': current_line_state,
                        'previous': previous_line_state,
                    }

        for id in add_ids:
            added_lines[id] = self.env['mrp.bom.line'].browse(int(id))

        for id in rem_ids:
            removed_lines[id] = previous_state[id]

        if edited_lines or added_lines or removed_lines:
            # Store tracked fields with their translation
            tracked_fields = {}
            for key in TRACKED_FIELDS:
                tracked_fields[key] = \
                    IrTranslation.get_field_string(BomLine._name)[key]

            self.message_post_with_view(
                'mrp_bom_replace_components.track_bom_template',
                values={
                    'tracked_fields': tracked_fields,
                    'edited_lines': edited_lines,
                    'added_lines': added_lines,
                    'removed_lines': removed_lines,
                },
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return True
