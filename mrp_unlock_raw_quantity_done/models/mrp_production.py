# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

import logging

from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # decoration-muted="is_done"
    # decoration-warning="quantity_done > product_uom_qty"
    # decoration-success="not is_done and quantity_done  < product_uom_qty"
    #     decoration-danger="not is_done and reserved_availability < product_uom_qty and product_uom_qty > reserved_availability">

    @api.multi
    def action_force_raw_quantity_done(self):
        """
        Using code written in `addons/mrp/views/mrp_production_views.xml` to
        print tree lines in decoration-danger, we re-apply the same filter
        and force assigned moves to done
        """
        for production_id in self:
            for move in production_id.move_raw_ids.filtered(
                lambda m: not m.is_done and m.state in
                ('partially_available', 'assigned')
            ):
                rounding = move.product_uom.rounding
                cmp1 = float_compare(
                    move.reserved_availability,
                    move.product_uom_qty,
                    precision_rounding=rounding
                )
                cmp2 = float_compare(
                    move.product_uom_qty,
                    move.reserved_availability,
                    precision_rounding=rounding
                )

                if cmp1 <= 0 and cmp2 > 0:
                    if move.state == 'assigned':
                        move.quantity_done = move.product_uom_qty
                    elif move.state == 'partially_available':
                        move.quantity_done = move.product_uom_qty
                        move.reserved_availability = 0

                    _logger.info(
                        "Force quantity done to {} on move {}: {}".format(
                            move.product_uom_qty, move.id,
                            move.product_id.display_name
                        )
                    )
