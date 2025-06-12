# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        help="Source Sale Order",
    )

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        for production, _vals in zip(record_ids, vals_list, strict=True):
            # use `sale_line_id` from `sale_mrp` module to retrieve partner_id
            if not production.sale_order_id:
                production.sale_order_id = production.sale_line_id.order_id
            # if no sale found then use `sale_line_id` stored in stock moves
            if not production.sale_order_id and production.move_finished_ids:
                move_ids = production.move_finished_ids
                while move_ids and not production.sale_order_id:
                    for move in move_ids:
                        if move.sale_line_id and move.sale_line_id.order_id:
                            production.sale_order_id = move.sale_line_id.order_id
                            break
                    move_ids = move_ids.mapped("move_dest_ids")
            if production.sale_order_id:
                production.partner_id = production.sale_order_id.partner_shipping_id
        return record_ids
