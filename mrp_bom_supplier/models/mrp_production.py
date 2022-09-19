# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _get_date_start(self, values):
        date_start = super()._get_date_start(values)
        bom_id = self.env['mrp.bom'].browse(values.get('bom_id'))
        if bom_id and bom_id.bom_line_ids:
            delay = max(bom_id.bom_line_ids.mapped("delay"))
            if delay:
                date_start += relativedelta(days=delay)
        return date_start
