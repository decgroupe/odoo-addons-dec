# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

import logging

from odoo import _, api, models
from odoo.exceptions import MissingError, UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        # Retry moves where PO/MO were canceled or deleted
        self.sudo()._retry_orphan_mto_moves(
            use_new_cursor=use_new_cursor, company_id=company_id
        )
        super(ProcurementGroup, self)._run_scheduler_tasks(
            use_new_cursor=use_new_cursor, company_id=company_id
        )

    @api.model
    def _retry_orphan_mto_moves(self, use_new_cursor=False, company_id=False):
        """Re-create procurements for 'make_to_order' moves if necessary.
        :param bool use_new_cursor: if set, use a dedicated cursor
        """
        if company_id and self.env.user.company_id.id != company_id:
            # To ensure that the company_id is taken into account for
            # all the processes triggered by this method
            # i.e. If a PO is generated by the run of the procurements the
            # sequence to use is the one for the specified company not the
            # one of the user's company
            self = self.with_context(company_id=company_id, force_company=company_id)
        moves_to_confirm = self._get_mto_moves_to_confirm()
        for move in moves_to_confirm:
            try:
                product_id = move.product_id
            except MissingError:
                # When this function is called from a loop, then since
                # _action_confirm is allowed to merge moves with same
                # characteristics, the next moves can be already deleted
                # from database, so we ignore them
                continue
            try:
                with self._cr.savepoint():
                    self._action_confirm_one_move(move)
            except UserError as error:
                self._log_exception(product_id, error.name)
        if use_new_cursor:
            self._cr.commit()

    @api.model
    def _get_mto_moves_to_confirm(self):
        # Search all active pickings
        picking_ids = self.env["stock.picking"].search(
            [("state", "in", ("waiting", "confirmed", "assigned"))]
        )
        # Select only valid moves
        picking_res = self._filter_mto_picking_moves_to_confirm(picking_ids)

        # Search all active manufacturing orders
        production_ids = self.env["mrp.production"].search(
            [("state", "not in", ("done", "cancel"))]
        )
        # Select only valid moves
        production_res = self._filter_mto_production_moves_to_confirm(production_ids)
        return picking_res + production_res

    @api.model
    def _filter_mto_picking_moves_to_confirm(self, picking_ids):
        return picking_ids.mapped("move_lines").filtered(
            lambda x: x.state not in ("done", "cancel")
            and x.procure_method == "make_to_order"
            and x.location_id == self.env.ref("stock.stock_location_stock")
            and x.created_purchase_line_id.id == False
            and x.move_orig_ids.purchase_line_id.id == False
            and x.created_production_id.id == False
            and x.created_mrp_production_request_id.id == False
            and x.move_orig_ids.ids == []
        )

    @api.model
    def _filter_mto_production_moves_to_confirm(self, production_ids):
        return production_ids.mapped("move_raw_ids").filtered(
            lambda x: x.state not in ("done", "cancel")
            and x.procure_method == "make_to_order"
            and x.location_id == self.env.ref("stock.stock_location_stock")
            and x.created_purchase_line_id.id == False
            and x.move_orig_ids.purchase_line_id.id == False
            and x.created_production_id.id == False
            and x.created_mrp_production_request_id.id == False
            and x.orderpoint_created_production_ids.ids == []
            and x.orderpoint_created_purchase_line_ids.ids == []
            and x.move_orig_ids.ids == []
        )

    @api.model
    def _action_confirm_one_move(self, move):
        move.ensure_one()
        _logger.info(
            "Execute method _action_confirm on {} ({})".format(
                move.product_id.display_name,
                move.picking_id.display_name,
            )
        )
        move._do_unreserve()
        if move.move_line_ids:
            raise ValidationError(
                _("Forcing draft state on move '%(move)s' is forbidden.", move=move)
            )
        move.write(
            {
                # Since Odoo 14.0, `_action_confirm` requires the move to be
                # in `draft` state
                "state": "draft",
            }
        )
        move._action_confirm()
