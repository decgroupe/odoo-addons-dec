# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026


from odoo import models
from odoo.tools.float_utils import float_compare

TRACKED_FIELDS = [
    "product_id",
    "partner_id",
    "buy_consumable",
    "landmark",
    "product_qty",
    "product_uom_id",
    "public_price",
    "unit_price",
    "cost_price",
]


def fix(res):
    """Ensure all dict keys are strings and all tuples become lists."""
    if res is None:
        return False
    elif isinstance(res, dict):
        return dict((str(key), fix(value)) for key, value in res.items())
    elif isinstance(res, list):
        return list(fix(x) for x in res)
    elif isinstance(res, tuple):
        return list(fix(x) for x in res)
    else:
        return res


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def write(self, vals):
        """Override write to track BoM line changes and post a note."""
        states = {}
        if "bom_line_ids" in vals:
            for rec in self:
                states[rec.id] = rec.get_track_state()
        res = super().write(vals)
        if "bom_line_ids" in vals:
            for rec in self:
                if rec.id in states:
                    rec.set_track_state(states[rec.id])
        return res

    def get_track_state(self):
        """Return a snapshot of the current BoM line field values."""
        self.ensure_one()
        vals = self.bom_line_ids.read(fields=TRACKED_FIELDS)
        res = {}
        for v in vals:
            line_id = v.pop("id")
            res[line_id] = v
        res = fix(res)
        return res

    def set_track_state(self, previous_state):
        """Compare previous state with current state and post a tracking note."""
        self.ensure_one()
        BomLine = self.env["mrp.bom.line"]
        IrModelFields = self.env["ir.model.fields"]
        edited_lines = {}
        added_lines = {}
        removed_lines = {}
        current_state = self.get_track_state()
        add_ids = list(set(current_state) - set(previous_state))
        rem_ids = list(set(previous_state) - set(current_state))
        for line_id in current_state:
            if line_id not in add_ids and line_id not in rem_ids:
                previous_line_state = previous_state[line_id]
                current_line_state = current_state[line_id]
                edited_fields = []
                for k in current_line_state:
                    if current_line_state[k] != previous_line_state[k]:
                        # specific case for floats, use float_compare to
                        # avoid detecting changes due to rounding issues
                        if isinstance(current_line_state[k], float):
                            digits = BomLine._fields[k]._digits
                            prec = self.env["decimal.precision"].precision_get(digits)
                            if float_compare(
                                current_line_state[k],
                                previous_line_state[k],
                                precision_digits=prec,
                            ):
                                edited_fields.append(k)
                        else:
                            edited_fields.append(k)
                if edited_fields:
                    edited_lines[line_id] = {
                        "line": self.env["mrp.bom.line"].browse(int(line_id)),
                        "edited_fields": edited_fields,
                        "current": current_line_state,
                        "previous": previous_line_state,
                    }
        for line_id in add_ids:
            added_lines[line_id] = self.env["mrp.bom.line"].browse(int(line_id))
        for line_id in rem_ids:
            removed_lines[line_id] = previous_state[line_id]
        if edited_lines or added_lines or removed_lines:
            # store tracked fields with their translation
            tracked_fields = {}
            for key in TRACKED_FIELDS:
                tracked_fields[key] = IrModelFields.get_field_string(BomLine._name)[key]
            self.message_post_with_source(
                "mrp_bom_track_components.track_bom_template",
                render_values={
                    "tracked_fields": tracked_fields,
                    "edited_lines": edited_lines,
                    "added_lines": added_lines,
                    "removed_lines": removed_lines,
                },
                subtype_id=self.env.ref("mail.mt_note").id,
            )
        return True
