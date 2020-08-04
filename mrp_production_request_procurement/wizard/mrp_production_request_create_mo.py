# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Aug 2020

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    def _create_procurement_group(self):
        """This function helps to get a production name like it is done in the
        original code: addons/mrp/models/mrp_production.py
        Returns:
            [type]: [description]
        """
        self.ensure_one()
        request_id = self.mrp_production_request_id
        if request_id.picking_type_id:
            mo_name = request_id.picking_type_id.sequence_id.next_by_id()
        else:
            mo_name = self.env['ir.sequence'].next_by_code('mrp.production')
        procurement_group_id = self.env["procurement.group"].create(
            {'name': mo_name}
        )
        return procurement_group_id

    @api.multi
    def _prepare_manufacturing_order(self):
        self.ensure_one()
        res = super()._prepare_manufacturing_order()
        request_id = self.mrp_production_request_id
        if request_id.mrp_production_ids:
            production_id = request_id.mrp_production_ids[0]
            procurement_group_id = production_id.procurement_group_id
            res['procurement_group_id'] = procurement_group_id.id
        else:
            procurement_group_id = self._create_procurement_group()
            res['procurement_group_id'] = procurement_group_id.id

        # Use procurement group name to generate a manufacturing order with
        # the same name or with an index if waiting quantity > 1
        if request_id.product_qty > 1 or request_id.manufacured_qty > 0:
            res['name'] = '{0}/{1:2d}'.format(
                procurement_group_id.name,
                request_id.manufacured_qty + 1,
            )
        else:
            res['name'] = procurement_group_id.name
        return res

    @api.multi
    def create_mo(self):
        self.ensure_one()
        action = super().create_mo()
        mo = self.env['mrp.production'].browse(action['res_id'])
        return action


class MrpProductionRequestCreateMoLine(models.TransientModel):
    _inherit = "mrp.production.request.create.mo.line"
