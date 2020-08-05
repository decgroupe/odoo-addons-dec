# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Aug 2020

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    def _get_production_name(self):
        self.ensure_one()
        """This function helps to get a production name like it is done in the
        original code: addons/mrp/models/mrp_production.py
        Returns:
            [string]: Production name
        """
        self.ensure_one()
        request_id = self.mrp_production_request_id
        if request_id.picking_type_id:
            res = request_id.picking_type_id.sequence_id.next_by_id()
        else:
            res = self.env['ir.sequence'].next_by_code('mrp.production')
        return res

    def _create_procurement_group(self):
        """This function helps to create a procurement group like it's done
        in the original code: addons/mrp/models/mrp_production.py
        Returns:
            [procurement.group]: [description]
        """
        self.ensure_one()
        procurement_group_id = self.env["procurement.group"].create(
            {'name': self._get_production_name()}
        )
        return procurement_group_id

    @api.multi
    def _prepare_manufacturing_order(self):
        self.ensure_one()
        res = super()._prepare_manufacturing_order()
        request_id = self.mrp_production_request_id
        # Generate and store a unique name as base for all production orders
        if not request_id.production_name:
            request_id.production_name = self._get_production_name()
        if request_id.use_common_procurement_group:
            if not request_id.common_procurement_group_id:
                request_id.common_procurement_group_id = self._create_procurement_group()
            res['procurement_group_id'] = request_id.common_procurement_group_id.id
        else:
            res['procurement_group_id'] = False

        # Use production_name as prefix to generate a manufacturing order with
        # the same name or with an index if waiting quantity > 1
        if request_id.product_qty > 1 or request_id.manufactured_qty > 0:
            res['name'] = '{0}/{1:2d}'.format(
                request_id.production_name,
                round(request_id.manufactured_qty) + 1,
            )
        else:
            res['name'] = request_id.production_name
        return res

    @api.multi
    def create_mo(self):
        self.ensure_one()
        action = super().create_mo()
        mo = self.env['mrp.production'].browse(action['res_id'])
        return action


class MrpProductionRequestCreateMoLine(models.TransientModel):
    _inherit = "mrp.production.request.create.mo.line"
