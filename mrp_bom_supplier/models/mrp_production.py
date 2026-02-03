# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def _update_earliest_date_planned(self, values):
        res = {}
        company_id = self.env["res.company"].browse(
            values.get("company_id", self.env.company.id)
        )
        manufacturing_lead = company_id.manufacturing_lead
        max_delay = 0
        date_start = fields.Datetime.to_datetime(values.get("date_start"))
        if date_start is None:
            date_start = self._get_default_date_start()
        # get max delay from BoM
        bom_id = self.env["mrp.bom"].browse(values.get("bom_id"))
        if bom_id and bom_id.bom_line_ids:
            max_delay = max(bom_id.bom_line_ids.mapped("delay"))
        # get max delay from raw moves
        if "move_raw_ids" in values:
            # TODO: use mapped values["move_raw_ids"][0][2]['product_id'] delays
            pass
        if max_delay:
            min_date_start = datetime.datetime.now() + relativedelta(days=max_delay)
            if min_date_start > date_start:
                date_start = min_date_start
        date_finished = fields.Datetime.to_datetime(values.get("date_finished"))
        if date_finished is None:
            date_finished = self._get_default_date_finished()

        if date_start:
            min_date_finished = date_start
            if bom_id and bom_id.produce_delay:
                min_date_finished += relativedelta(days=bom_id.produce_delay)
            if manufacturing_lead:
                min_date_finished += relativedelta(days=manufacturing_lead)
            if not date_finished or (
                date_finished and min_date_finished > date_finished
            ):
                date_finished = min_date_finished

        if date_start:
            res["date_start"] = date_start
        if date_finished:
            res["date_finished"] = date_finished

        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            earliest_dates = self._update_earliest_date_planned(vals)
            if earliest_dates:
                vals.update(earliest_dates)
        record_ids = super().create(vals_list)
        return record_ids

    def write(self, vals):
        if "date_start" in vals:
            earliest_dates = self._update_earliest_date_planned(vals.copy())
            if earliest_dates:
                vals.update(earliest_dates)
        res = super().write(vals)
        return res
