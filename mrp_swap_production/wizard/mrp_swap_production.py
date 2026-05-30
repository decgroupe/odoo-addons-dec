# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def _logger_print(*args):
    """Log a wizard trace line."""
    _logger.info(" ".join(str(x) for x in list(args)))


class MrpSwapProduction(models.TransientModel):
    _name = "mrp.swap.production"
    _description = "Swap two manufacturing orders"

    this_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="This",
        required=True,
        readonly=True,
        domain=[],
    )
    product_id = fields.Many2one(
        related="this_production_id.product_id",
        string="Product",
        required=True,
        readonly=True,
    )
    other_production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Other",
        required=True,
        readonly=False,
    )
    swap_line_ids = fields.Many2many(
        comodel_name="mrp.swap.production.line",
        string="Swap Lines",
    )

    @api.model
    def default_get(self, fields_list):
        """Pre-fill the wizard from the active manufacturing order."""
        defaults = super().default_get(fields_list)
        active_id = self.env.context.get("active_id")
        if active_id and "this_production_id" in fields_list:
            defaults.setdefault("this_production_id", active_id)
        return defaults

    @api.onchange("other_production_id")
    def onchange_other_production_id(self):
        """Prepare the list of production pairs to swap."""
        mapping = {}
        self.swap_line_ids.unlink()
        if not self.other_production_id:
            return

        def _map_subproduction_with_product(production_id):
            """Collect subproductions indexed by finished product."""
            sub_production_ids = production_id.move_raw_ids.mapped(
                "move_orig_ids"
            ).mapped("production_id")
            for p in sub_production_ids:
                if p.product_id not in mapping:
                    mapping[p.product_id] = []
                mapping[p.product_id].append(p)

        _map_subproduction_with_product(self.this_production_id)
        _map_subproduction_with_product(self.other_production_id)

        # pre-fill the main production pair first
        vals = {
            "product_id": self.product_id.id,
            "from_production_id": self.this_production_id.id,
            "to_production_id": self.other_production_id.id,
            "swap_final_moves": True,
        }
        line_ids = self.env["mrp.swap.production.line"].create(vals)

        for product_id, production_ids in mapping.items():
            if len(production_ids) == 2:
                vals = {
                    "product_id": product_id.id,
                    "from_production_id": production_ids[0].id,
                    "to_production_id": production_ids[1].id,
                }
                line_ids += self.env["mrp.swap.production.line"].create(vals)
        self.swap_line_ids += line_ids

    @api.model
    def _get_fields_that_must_be_identical(self):
        """Return fields that must match before records can be swapped."""
        return {
            "mrp.production": [
                "product_id",
                "product_qty",
                "product_uom_id",
                "allow_timesheets",
            ],
            "mrp.production.request": [
                "product_qty",
                "product_uom_id",
            ],
        }

    @api.model
    def log_field(self, name, obj):
        """Log the current value of a field on a record."""
        cache_value = obj[name]
        if isinstance(cache_value, models.Model):
            for value in cache_value:
                _logger_print("  -", name, value, value.display_name)
        else:
            _logger_print("-", name, cache_value)
        if not cache_value:
            _logger_print("-", name, "is empty ⚠️", cache_value)

    @api.model
    def swap_fields(self, name, this, other):
        """Swap a field value between two records when they differ."""
        if this[name] == other[name]:
            _logger_print(name, "are equals ->", this[name])
            return
        _logger_print("Field value before:")
        self.log_field(name, this)
        self.log_field(name, other)

        # cache values before assigning them to the other record
        cache_this_value = this[name]
        cache_other_value = other[name]
        this[name] = cache_other_value
        other[name] = cache_this_value
        _logger_print("Field value after:")
        self.log_field(name, this)
        self.log_field(name, other)

    def _pre_swap_production_check(self, moa_id, mob_id):
        """Validate that two manufacturing orders can be swapped."""
        for field in self._get_fields_that_must_be_identical()["mrp.production"]:
            if moa_id[field] != mob_id[field]:
                raise UserError(
                    self.env._(
                        "`%(field)s` value must be identical for %(first)s "
                        "and %(second)s",
                        field=field,
                        first=moa_id.display_name,
                        second=mob_id.display_name,
                    )
                )
        self._pre_swap_production_request_check(
            moa_id.mrp_production_request_id,
            mob_id.mrp_production_request_id,
        )
        self._check_allowed_timesheet_swap(moa_id, mob_id)
        self._check_allowed_timesheet_swap(mob_id, moa_id)

    def _pre_swap_production_request_check(self, pra_id, prb_id):
        """Validate that production request linkage is consistent for a swap."""
        if not pra_id and not prb_id:
            # ignore if both orders are not issued from a production request
            return
        if (pra_id and not prb_id) or (prb_id and not pra_id):
            raise UserError(
                self.env._(
                    "Both production orders must be issued from a production request"
                )
            )

    def swap_production(self, moa_id, mob_id, swap_final_moves=False):
        """Swap manufacturing-order metadata and linked request content."""
        _logger_print(
            "Swapping",
            moa_id.display_name,
            "as THIS with",
            mob_id.display_name,
            "as OTHER",
        )
        self.swap_fields("origin", moa_id, mob_id)
        self.swap_fields("sale_order_id", moa_id, mob_id)
        self.swap_fields("partner_id", moa_id, mob_id)
        self.swap_fields(
            "date_planned_start",
            moa_id.with_context(force_date=True),
            mob_id.with_context(force_date=True),
        )
        self.swap_fields("date_planned_finished", moa_id, mob_id)
        self.swap_fields("note", moa_id, mob_id)
        self.swap_fields(
            "project_id",
            moa_id.with_context(ignore_constrains_project_timesheets=True),
            mob_id.with_context(ignore_constrains_project_timesheets=True),
        )
        if swap_final_moves:
            self.swap_fields(
                "move_dest_ids", moa_id.move_finished_ids, mob_id.move_finished_ids
            )
        self.swap_production_request_content(
            moa_id.mrp_production_request_id,
            mob_id.mrp_production_request_id,
            swap_final_moves,
        )
        self.update_timesheet_project(moa_id)
        self.update_timesheet_project(mob_id)
        self.message_post_swap(moa_id, mob_id)

    def _check_allowed_timesheet_swap(self, production_id, other_production_id):
        """Ensure the swap does not break timesheet/project constraints."""
        if production_id.timesheet_ids and not production_id.project_id:
            raise UserError(
                self.env._(
                    "Production order %(production)s with timesheet entries must "
                    "have a project",
                    production=production_id.display_name,
                )
            )
        if (
            production_id.timesheet_ids
            and production_id.project_id
            and not production_id.allow_timesheets
        ):
            raise UserError(
                self.env._(
                    "Production order %(production)s with timesheet entries must "
                    "have `allow_timesheets` enabled",
                    production=production_id.display_name,
                )
            )
        if (
            production_id.timesheet_ids
            and production_id.project_id
            and not other_production_id.project_id
        ):
            raise UserError(
                self.env._(
                    "Production order %(production)s must have a project",
                    production=other_production_id.display_name,
                )
            )

    @api.model
    def update_timesheet_project(self, production_id):
        """Move related tasks and timesheets to the production project."""
        _logger_print(
            "Updating timesheets of production order", production_id.display_name
        )
        task_ids = production_id.timesheet_ids.mapped("task_id")
        _logger_print(
            "Assigning project_id to task_ids", production_id.project_id, task_ids
        )
        task_ids.write({"project_id": production_id.project_id.id})
        _logger_print(
            "Assigning project_id to timesheet_ids",
            production_id.project_id,
            production_id.timesheet_ids,
        )
        production_id.timesheet_ids.write({"project_id": production_id.project_id.id})

    @api.model
    def swap_production_request_content(self, pra_id, prb_id, swap_final_moves):
        """Swap compatible linked production-request data."""
        if not pra_id and not prb_id:
            # ignore if both orders are not issued from a production request
            return
        for field in self._get_fields_that_must_be_identical()[
            "mrp.production.request"
        ]:
            if pra_id[field] != prb_id[field]:
                raise UserError(
                    self.env._(
                        "`%(field)s` value must be identical for %(first)s "
                        "and %(second)s",
                        field=field,
                        first=pra_id.display_name,
                        second=prb_id.display_name,
                    )
                )
        self.swap_fields("sale_order_id", pra_id, prb_id)
        self.swap_fields("partner_id", pra_id, prb_id)
        self.swap_fields("description", pra_id, prb_id)
        if swap_final_moves:
            self.swap_fields("origin", pra_id, prb_id)
            self.swap_fields("date_planned_start", pra_id, prb_id)
            self.swap_fields("date_planned_finished", pra_id, prb_id)

            # swap the stock moves that point back to each request
            pra_id_move = self.env["stock.move"].search(
                [("created_mrp_production_request_id", "=", pra_id.id)], limit=1
            )
            prb_id_move = self.env["stock.move"].search(
                [("created_mrp_production_request_id", "=", prb_id.id)], limit=1
            )
            self.swap_fields(
                "created_mrp_production_request_id", pra_id_move, prb_id_move
            )
        self.message_post_swap(pra_id, prb_id)

    def message_post_swap(self, obja_id, objb_id):
        """Post a chatter entry on both swapped records."""

        def _get_link(obj_id):
            """Build a lightweight chatter link for the target record."""
            return '<a href="#" data-oe-model="%s" data-oe-id="%d">%s</a>' % (
                obj_id._name,
                obj_id.id,
                obj_id.name,
            )

        message = self.env._("🔄 Swapped with %(record)s", record=_get_link(objb_id))
        obja_id.message_post(body=message)
        message = self.env._("🔄 Swapped with %(record)s", record=_get_link(obja_id))
        objb_id.message_post(body=message)

    def do_swap(self):
        """Validate all swap lines and execute the requested swaps."""
        self.ensure_one()
        for line in self.swap_line_ids:
            self._pre_swap_production_check(
                line.from_production_id,
                line.to_production_id,
            )
        for line in self.swap_line_ids:
            self.swap_production(
                line.from_production_id,
                line.to_production_id,
                line.swap_final_moves,
            )
