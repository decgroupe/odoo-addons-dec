# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from collections import defaultdict
from datetime import datetime

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, ormcache
from odoo.tools.float_utils import float_compare

from odoo.addons.tools_miscellaneous.tools.html_helper import (
    b,
    div,
    format_hd,
    li,
    ul,
)

MOVE_STATE_SYMBOLS = {
    "draft": "🏳️",
    "waiting": "⛓️",
    "confirmed": "⏳",
    "partially_available": "✴️",
    "assigned": "✳️",
    "done": "✅",
    "cancel": "❌",
}


class StockMove(models.Model):
    _inherit = "stock.move"

    pick_status = fields.Html(
        string="Picking Upstream Status",
        compute="_compute_pick_status",
        default="",
        store=False,
    )
    final_location = fields.Char(
        string="Final location",
        compute="_compute_final_location",
        help="Get final location name",
        readonly=True,
    )
    action_view_created_item_visible = fields.Boolean(
        string="Show Link to Created Item",
        compute="_compute_action_view_created_item_visible",
        readonly=True,
    )
    product_activity_id = fields.Many2one(
        comodel_name="mail.activity",
        string="Related Activity",
        compute="_compute_product_activity_id",
    )
    state_symbol = fields.Char(compute="_compute_state_symbol")

    @api.depends("state")
    def _compute_state_symbol(self):
        for rec in self:
            rec.state_symbol = MOVE_STATE_SYMBOLS.get(rec.state, "")

    def _get_mto_pick_status(self, html=False):
        return self._get_mto_status(html)

    def _get_mts_pick_status(self, html=False):
        return self._get_mts_status(html)

    def get_pick_status(self, html=False):
        status = []
        if self.procure_method == "make_to_order":
            status += self._get_mto_pick_status(html)
        elif self.procure_method == "make_to_stock":
            status += self._get_mts_pick_status(html)

        upstream_moves = self._get_upstreams()
        for move in upstream_moves:
            upstream_status = []
            if move.procure_method == "make_to_order":
                upstream_status += move._get_mto_pick_status(html)
            elif move.procure_method == "make_to_stock":
                upstream_status += move._get_mts_pick_status(html)
            # Check if status is not a duplicate, it could happen in some
            # cases where we can have self.created_production_id identical to
            # move.production_id
            for upstream_status_line in upstream_status:
                if upstream_status_line not in status:
                    status.append(upstream_status_line)

        if self.picking_code == "incoming":
            for group_id in self.move_dest_ids.mapped("group_id"):
                head, desc = group_id.get_head_desc()
                head = "📥" + head
                status.append(format_hd(head, desc, html))

        if self.picking_code == "outgoing":
            for group_id in self.move_orig_ids.mapped("group_id"):
                head, desc = group_id.get_head_desc()
                head = "📤" + head
                status.append(format_hd(head, desc, html))

        status += self._get_assignable_status(html)
        return self._format_status_header(status, html)

    @api.depends(
        "procure_method",
        "quantity",
        "state",
        "action_view_created_item_visible",
    )
    def _compute_pick_status(self):
        for move in self:
            move.pick_status = move.get_pick_status(html=True)

    @api.depends("move_dest_ids", "location_dest_id", "product_id")
    def _compute_final_location(self):
        for rec in self:
            rec.final_location = rec.location_dest_id.name
            move_dest_id = rec.move_dest_ids and rec.move_dest_ids[0] or False
            if move_dest_id and rec.product_id.id == move_dest_id.product_id.id:
                if not move_dest_id.final_location:
                    # Force recompute since Odoo framework does not
                    # seems to do it properly ...
                    move_dest_id._compute_final_location()
                final_location = move_dest_id.final_location
                if final_location:
                    if self.env.is_admin():
                        rec.final_location += " > " + final_location
                    else:
                        rec.final_location = final_location

    @api.model
    @ormcache()
    def _get_product_template_ir_model_id(self):
        """This method returns an ID so it can be cached."""
        ir_model = (
            self.env["ir.model"]
            .sudo()
            .search([("model", "=", self.product_id.product_tmpl_id._name)])
        )
        return ir_model.id

    @api.model
    @ormcache()
    def _get_warning_activity_type_id(self):
        """This method returns an ID so it can be cached."""
        activity_type_id = self.env.ref("mail.mail_activity_data_warning")
        return activity_type_id.id

    @api.depends("product_id")
    def _compute_product_activity_id(self):
        for move in self:
            domain = [
                ("res_id", "=", move.product_id.product_tmpl_id.id),
                (
                    "res_model_id",
                    "=",
                    move._get_product_template_ir_model_id(),
                ),
                (
                    "activity_type_id",
                    "=",
                    move._get_warning_activity_type_id(),
                ),
            ]
            activity = move.env["mail.activity"].search(domain, limit=1)
            move.product_activity_id = activity

    def _get_mto_created_items(self):
        self.ensure_one()
        res = defaultdict(lambda: {"priority": 0, "record": False})
        if self.product_activity_id:
            action = self.product_activity_id.action_view()
            res["stock_traceability"] = {
                "priority": 10,
                "record": self.product_activity_id,
                "action": action,
            }
        return res

    def _get_mto_created_item(self):
        """Get the nearest created item linked to this move."""
        self.ensure_one()
        res = self._get_mto_created_items()
        if res:
            return max(res.values(), key=lambda x: x["priority"])
        return False

    def action_view_created_item(self):
        """Generate an action that will match the nearest object linked
        to this move. It is used to open a Purchase, Sale, etc.
        """
        self.ensure_one()
        action = False
        created_item = self._get_mto_created_item()
        if created_item:
            action = created_item["action"]
        return action

    def _compute_action_view_created_item_visible(self):
        """Compute the boolean field `action_view_created_item_visible` that will be
        used to display or not a link to the created item.
        It is now useless to inherits from `is_action_view_created_item_visible` since
        everything is done from `_get_mto_created_item`
        """
        for move in self:
            created_item = move._get_mto_created_item()
            move.action_view_created_item_visible = bool(created_item)

    def action_open_stock_move_form(self):
        action = {
            "type": "ir.actions.act_window",
            "name": "Open Advanced Stock Move Form View",
            "display_name": " Stock Move Advanced View",
            "res_model": "stock.move",
            "context": "{}",
            "domain": "[]",
            "filter": False,
            "target": "new",
            "view_id": self.env.ref("stock.view_move_form").id,
            "view_mode": "form",
            "view_type": "form",
        }
        action["res_id"] = self.id
        return action

    def get_head_desc(self):
        state = dict(self._fields["state"]._description_selection(self.env)).get(
            self.state
        )
        if self.procure_method == "make_to_order":
            # the "alien" case: an MTO should never be used to get head description
            # since it should always be linked to a created item (sale order,
            # purchase order, etc.) but we need to handle the case for testing purposes
            head = "👽MTO"
        else:
            head = f"📦{self.env._('Stock')}"
        desc = f"{self.state_symbol}{state}"
        return head, desc

    def _get_stock_location(self, html=False):
        def try_append_loc(location, loc):
            if loc:
                if html:
                    loc = b(loc)
                location.append(loc)

        location = []
        try_append_loc(location, self.product_id.loc_rack)
        try_append_loc(location, self.product_id.loc_row)
        try_append_loc(location, self.product_id.loc_case)
        if not location:
            location = [self.env._("Not Set")]
        head = f"🗺️{self.env._('Location')}"
        desc = " . ".join(location)
        return head, desc

    def _get_mto_status(self, html=False):
        res = []
        created_item = self._get_mto_created_item()
        if created_item:
            for record_id in created_item["record"]:
                head, desc = record_id.get_head_desc()
                res.append(format_hd(head, desc, html))
        else:
            # Since the current status is unknown, fallback using mts status
            # to print archive when exists
            res.extend(self._get_mts_status(html))

        # Add parent picking informations
        if len(self.move_orig_ids.ids) == 1:
            picking_id = self.move_orig_ids.picking_id
            if picking_id:
                head = f"🚚 {self.move_orig_ids.picking_id.name}"
                desc = datetime.strftime(
                    picking_id.scheduled_date, DEFAULT_SERVER_DATE_FORMAT
                )
                res.append(format_hd(head, desc, html))

        return res

    def _get_mts_pre_archive(self):
        return False

    def _get_mts_status(self, html=False):
        res = []

        head, desc = self.get_head_desc()
        res.append(format_hd(head, desc, html))

        stock_location = self.env.ref("stock.stock_location_stock")

        # Print location only when destination moves are for stock
        # or if this move is the final one to stock
        if self.move_dest_ids:
            same_destination = all(
                x.id == stock_location.id
                for x in self.move_dest_ids.mapped("location_dest_id")
            )
            different_product = any(
                x.id != self.product_id.id
                for x in self.move_dest_ids.mapped("product_id")
            )
        else:
            same_destination = self.location_dest_id.id == stock_location.id
            different_product = False

        if same_destination or different_product:
            head, desc = self._get_stock_location(html)
            res.append(format_hd(head, desc, html=False))

        pre_archive = self._get_mts_pre_archive()
        if pre_archive:
            res.append(f"{pre_archive}{self.env._('canceled')}")

        if (
            self.state not in ("assigned", "done", "cancel")
            and self.product_activity_id
        ):
            head, desc = self.product_activity_id.get_head_desc()
            res.append(format_hd(head, desc, html))

        return res

    def _get_assignable_status(self, html=False):
        Quant = self.env["stock.quant"]
        res = []
        if (
            self.state in ("waiting", "confirmed")
            and self.move_orig_ids
            and all(orig.state in ("done", "cancel") for orig in self.move_orig_ids)
        ):
            rounding = self.product_id.uom_id.rounding
            needed_quantity = self.product_qty - sum(
                self.move_line_ids.mapped("product_qty")
            )
            available_quantity = Quant._get_available_quantity(
                self.product_id,
                self.location_id,
                strict=True,
                allow_negative=True,
            )
            if (
                float_compare(
                    needed_quantity, available_quantity, precision_rounding=rounding
                )
                > 0
            ):
                head = f"⚠️{self.env._('Reservation issue')}"
                desc = "\n" + self.env._(
                    "%(needed_quantity)g needed but %(available_quantity)g available",
                    needed_quantity=needed_quantity,
                    available_quantity=available_quantity,
                )
                hd = format_hd(head, desc, html)
                if html:
                    hd = div(hd, "alert-warning")
                res.append(hd)
        return res

    def _get_upstreams(self, ensure_same_product=True):
        res = self.env["stock.move"]
        if self.move_orig_ids:
            for move in self.move_orig_ids:
                if ensure_same_product:
                    if move.product_id == self.product_id:
                        res += move
                else:
                    res += move
        return res

    def _get_pre_header(self):
        product_type = dict(
            self.product_id._fields["type"]._description_selection(self.env)
        ).get(self.product_id.type)
        head = f"{self.product_id.type_symbol}{product_type}"
        return head

    def _format_status_header(self, status, html=False):
        head = self._get_pre_header()
        # WARNING: This will also checks for request.session.debug
        if self.env.user.has_group("base.group_no_one"):
            head = f"{head} (ID: {self.id})"
        status.insert(0, head)
        if html:
            list_as_html = "".join(list(map(li, status)))
            return div(ul(list_as_html), "d_move d_move_" + self.state)
        else:
            return "\n".join(status)

    def action_close_dialog(self):
        return {"type": "ir.actions.act_window_close"}
