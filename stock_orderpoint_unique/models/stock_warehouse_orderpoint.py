# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    # This SQL constraint blocks the use of the "active" field
    # but I think it's not very useful to have such an "active" field
    # on orderpoints ; when you think the order point is bad, you update
    # the min/max values, you don't de-active it !
    _sql_constraints = [
        (
            'company_wh_location_product_unique',
            'unique(company_id, warehouse_id, location_id, product_id)',
            'An orderpoint already exists for the same company, same '
            'warehouse, same stock location and same product.',
        )
    ]
