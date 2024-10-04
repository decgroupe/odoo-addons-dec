# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

import datetime

from odoo import _, api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.model
    def _update_earliest_date_planned(self, values):
        res = {}
        max_delay = 0
        date_start = fields.Datetime.to_datetime(values.get("date_planned_start"))
        if date_start is None:
            date_start = self._get_default_date_planned_start()
        # get max delay from BoM
        bom_id = self.env["mrp.bom"].browse(values.get("bom_id"))
        if bom_id and bom_id.bom_line_ids:
            max_delay = max(bom_id.bom_line_ids.mapped("delay"))
        # get max delay from raw moves
        if "move_raw_ids" in values:
            # TODO: use mapped values["move_raw_ids"][0][2]['product_id'] delays
            pass
        if max_delay:
            min_date_start = datetime.datetime.now() + datetime.timedelta(
                days=max_delay
            )
            if min_date_start > date_start:
                res["date_planned_start"] = min_date_start
        date_finished = fields.Datetime.to_datetime(values.get("date_planned_finished"))
        if date_finished is None:
            date_finished = self._get_default_date_planned_finished()
        # recompute finished date only if start date has been updated
        if "date_planned_start" in res:
            # keep only mandatory values
            data = {k: values[k] for k in ["product_id", "company_id"]}
            # use start date from our computation
            data["date_planned_start"] = res["date_planned_start"]
            # play @api.onchange (_onchange_date_planned_start)
            vals = self.env["mrp.production"].play_onchanges(
                data, ["date_planned_start"]
            )
            res["date_planned_finished"] = vals["date_planned_finished"]
        return res

    @api.model
    def create(self, values):
        earliest_dates = self._update_earliest_date_planned(values)
        if earliest_dates:
            values.update(earliest_dates)
            # TODO: also update dates in `move_raw_ids`
        production = super(MrpProduction, self).create(values)
        return production

    def write(self, vals):
        if "date_planned_start" in vals:
            data = vals.copy()
            data.update(
                {
                    "company_id": self.company_id.id,
                    "product_id": self.product_id.id,
                    "bom_id": self.bom_id.id,
                }
            )
            earliest_dates = self._update_earliest_date_planned(data)
            if earliest_dates:
                vals.update(earliest_dates)
        res = super(MrpProduction, self).write(vals)
        return res
