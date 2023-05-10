# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class PurchaseOrderMerge(models.TransientModel):
    _name = "purchase.order.merge"
    _description = "Merge Purchase Order"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Vendor",
    )
    order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase Order",
    )
    origin_order_ids = fields.Many2many(
        comodel_name="purchase.order",
        string="Origin Orders",
        readonly=True,
    )
    origin_group_ids = fields.Many2many(
        comodel_name="procurement.group",
        string="Origin Procurement Groups",
        compute="_compute_origin_group_ids",
    )
    group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement Group",
        help="Multiple orders means multiple procurement groups. You need to "
        "select which group will be used in the newly created order.",
    )
    pre_process = fields.Selection(
        selection=[
            ("create", "Create new order"),
            ("merge", "Merge orders on selected order"),
        ],
        string="Merge Mode",
        default="create",
    )
    post_process = fields.Selection(
        selection=[
            ("cancel", "Cancel"),
            ("delete", "Delete"),
        ],
        string="Remaining Order(s)",
        default="cancel",
    )
    merge_quantities = fields.Boolean(
        string="Merge Quantities",
        help="If checked, all lines with the same product will be merged "
        "and their quantities will be added",
    )

    @api.depends("origin_order_ids")
    def _compute_origin_group_ids(self):
        for rec in self:
            po_lines = rec.origin_order_ids.mapped("order_line")
            rec.origin_group_ids = po_lines.mapped("procurement_group_id")

    def _check_selection_count(self, order_ids):
        if len(order_ids) < 2:
            raise UserError(_("Please select two or more orders in the list view"))

    def _check_selection_state(self, order_ids):
        PurchaseOrder = self.env["purchase.order"]
        selection_states = order_ids.mapped("state")
        mergeable_states = PurchaseOrder._get_mergeable_states()
        diff_states = set(selection_states) - set(mergeable_states)
        if diff_states:
            display_states = {}
            # Get human readable incompatible state names
            for state in diff_states:
                display_state = dict(
                    PurchaseOrder._fields["state"]._description_selection(self.env)
                ).get(state)
                display_states[state] = display_state
            invalid_po = []
            for order_id in order_ids.filtered(lambda p: p.state in diff_states):
                invalid_po.append(
                    "{} state is {}".format(
                        order_id.display_name, display_states[order_id.state]
                    )
                )

            raise UserError(
                _("Selection contains order(s) in incompatible states:\n%s")
                % ("\n - ".join([""] + invalid_po))
            )

    def _check_selection_partners(self, order_ids):
        partner_ids = order_ids.mapped("partner_id")
        if len(partner_ids) > 1:
            raise UserError(
                _(
                    "All orders must have the same supplier.\n"
                    "You have selected orders from these partners:\n%s"
                )
                % ("\n - ".join([""] + partner_ids.mapped("display_name")))
            )

    def _check_selection_compatibility(self, origin_order_ids):
        self._check_selection_count(origin_order_ids)
        self._check_selection_state(origin_order_ids)
        self._check_selection_partners(origin_order_ids)

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_ids = self._context.get("active_ids")
        active_model = self._context.get("active_model")

        if active_model == "purchase.order" and active_ids:
            origin_order_ids = self.env["purchase.order"].browse(active_ids)
            # Ensure selected data is valid
            self._check_selection_compatibility(origin_order_ids)
            # Assign wizard default values
            partner_id = origin_order_ids.mapped("partner_id")
            rec.update(
                {
                    "partner_id": partner_id.id,
                    "origin_order_ids": [(6, 0, origin_order_ids.ids)],
                }
            )
        return rec

    @api.onchange("order_id")
    def _onchange_order_id(self):
        self.group_id = self.order_id.group_id

    def _same_product(self, l1, l2):
        res = l1.product_id == l2.product_id
        return res

    def _same_uom(self, l1, l2):
        res = l1.product_uom == l2.product_uom
        return res

    def _same_price(self, l1, l2):
        dp = self.env["decimal.precision"].precision_get("Product Price")
        res = float_compare(l1.price_unit, l2.price_unit, precision_digits=dp) == 0
        return res

    def _same_procurement(self, l1, l2):
        res = l1.procurement_group_id == l2.procurement_group_id
        return res

    def _same_taxes(self, l1, l2):
        res = l1.taxes_id == l2.taxes_id
        return res

    def _same_name(self, l1, l2):
        res = l1.name == l2.name
        return res

    def _same_lines(self, l1, l2):
        if (
            self._same_product(l1, l2)
            and self._same_uom(l1, l2)
            and self._same_price(l1, l2)
            and self._same_procurement(l1, l2)
            and self._same_taxes(l1, l2)
            and self._same_name(l1, l2)
        ):
            return True
        else:
            return False

    def _try_merging(self, line):
        match_line = False
        if self.order_id.order_line:
            for po_line in self.order_id.order_line:
                if self._same_lines(line, po_line):
                    match_line = po_line
                    break
        if match_line:
            match_line.product_qty += line.product_qty
            match_line.move_ids += line.move_ids
            match_line.move_dest_ids += line.move_dest_ids
            return True
        else:
            return False

    def _pre_process_create(self):
        vals = self.env["purchase.order"].play_onchanges(
            {
                "partner_id": self.partner_id.id,
                "date_order": min(self.origin_order_ids.mapped("date_order")),
            },
            ["partner_id"],
        )
        self.order_id = self.env["purchase.order"].create(vals)
        self._pre_process_merge()

    def _pre_process_merge(self):
        # Remove selected order from list
        self.origin_order_ids -= self.order_id
        sequences = self.order_id.order_line.mapped("sequence")
        if sequences:
            sequence = max(sequences)
        else:
            sequence = 0
        po_line_unlink_ids = self.env["purchase.order.line"]
        for order in self.origin_order_ids:
            for line in order.order_line:
                if self.merge_quantities:
                    merged = self._try_merging(line)
                    if merged:
                        po_line_unlink_ids += line
                else:
                    merged = False
                if not merged:
                    sequence += 1
                    line.write(
                        {
                            "sequence": sequence,
                            "order_id": self.order_id.id,
                        }
                    )
        if po_line_unlink_ids:
            po_line_unlink_ids.unlink()
        self._set_origin()
        self.order_id.message_post_with_view(
            views_or_xmlid="purchase_merge.merged_with_template",
            values={
                "order_ids": self.origin_order_ids,
            },
            subtype_id=self.env.ref("mail.mt_note").id,
        )

    def _set_origin(self):
        if self.order_id.origin:
            self.order_id.origin += ","
        else:
            self.order_id.origin = ""
        display_names = list(set(self.origin_order_ids.mapped("display_name")))
        self.order_id.origin += ",".join(display_names)

    def _post_process_cancel(self):
        for order_id in self.origin_order_ids:
            order_id.message_post_with_view(
                views_or_xmlid="purchase_merge.merged_to_template",
                values={
                    "order_id": self.order_id,
                },
                subtype_id=self.env.ref("mail.mt_note").id,
            )
            order_id.button_cancel()

    def _post_process_delete(self):
        self._post_process_cancel()
        for order_id in self.origin_order_ids:
            order_id.sudo().unlink()

    def action_merge(self):
        if self.pre_process == "create":
            self._pre_process_create()
        elif self.pre_process == "merge":
            self._pre_process_merge()

        if self.post_process == "cancel":
            self._post_process_cancel()
        elif self.post_process == "delete":
            self._post_process_delete()

        action_vals = {
            "name": _("Purchase Orders (after merge)"),
            "view_type": "form",
            "view_mode": "form",
            "res_id": self.order_id.id,
            "res_model": "purchase.order",
            "view_id": False,
            "type": "ir.actions.act_window",
        }
        return action_vals
