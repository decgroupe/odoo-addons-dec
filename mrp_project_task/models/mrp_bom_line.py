# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import api, fields, models, _


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    # Copy from odoo/addons/sale_timesheet/models/sale_order.py
    def _convert_qty_company_hours(self):
        company_time_uom_id = self.env.user.company_id.project_time_mode_id
        product_uom = self.product_uom_id
        product_uom_qty = self.product_qty
        if product_uom.id != company_time_uom_id.id and product_uom.category_id.id == company_time_uom_id.category_id.id:
            planned_hours = product_uom._compute_quantity(
                product_uom_qty, company_time_uom_id
            )
        else:
            uom_hour = self.env.ref('uom.product_uom_hour')
            if uom_hour and product_uom.id != uom_hour.id and product_uom.category_id.id == uom_hour.category_id.id:
                planned_hours = product_uom._compute_quantity(
                    product_uom_qty, uom_hour
                )
            else:
                planned_hours = product_uom_qty
        return planned_hours
