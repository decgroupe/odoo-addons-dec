# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    # addons/stock/models/stock_picking.py
    picking_ids = fields.One2many(
        comodel_name='stock.picking',
        inverse_name='group_id',
    )
    # addons/stock/models/stock_warehouse.py
    orderpoint_ids = fields.One2many(
        comodel_name='stock.warehouse.orderpoint',
        inverse_name='group_id',
    )
    # addons/stock/models/stock_rule.py
    stock_rule_ids = fields.One2many(
        comodel_name='stock.rule',
        inverse_name='group_id',
    )
    # addons/stock/models/stock_move.py
    stock_move_ids = fields.One2many(
        'stock.move',
        'group_id',
    )
    # addons/sale_stock/models/sale_order.py
    sale_order_ids = fields.One2many(
        'sale.order',
        'procurement_group_id',
    )
    # addons/purchase_stock/models/purchase.py
    purchase_order_ids = fields.One2many(
        'purchase.order',
        'group_id',
    )
    # addons/mrp/models/mrp_production.py
    mrp_production_ids = fields.One2many(
        'mrp.production',
        'procurement_group_id',
    )
