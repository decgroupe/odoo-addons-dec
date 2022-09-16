# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, values):
        self._prepare_mo_values(values)
        production_id = super(MrpProduction, self).create(values)
        return production_id

    def _override_date_planned(self, values):
        if not values.get('date_planned_start'):
            res = True
        elif values.get('date_planned_start') == \
            values.get('date_planned_finished'):
            res = True
        else:
            res = False
        return res

    def _get_date_start(self, values):
        """ Use default `date_planned_start` or the `today`, if not set, as 
            default start date.
            The purpose of this method is to be overriden.
        """
        if values.get('date_planned_start'):
            res = values.get('date_planned_start')
        else:
            res = fields.Date.context_today(self)
        return res

    def _get_date_finished(self, date_start, product_id, company_id):
        """ Use inverse method of `_get_date_planned` defined in
            odoo/addons/mrp/models/stock_rule.py
        """
        date_planned = fields.Datetime.from_string(date_start)
        if product_id:
            date_planned = date_planned + relativedelta(
                days=product_id.produce_delay or 0.0
            )
        if company_id:
            date_planned = date_planned - relativedelta(
                days=company_id.manufacturing_lead
            )
        return date_planned

    def _prepare_mo_values(self, values):
        if self._override_date_planned(values):
            product_id = self.env['product.product'].browse(
                values.get('product_id')
            )
            company_id = self.env['res.company'].browse(
                values.get('company_id')
            )
            date_start = self._get_date_start(values)
            values['date_planned_start'] = date_start
            values['date_planned_finished'] = self._get_date_finished(
                date_start, product_id, company_id
            )
