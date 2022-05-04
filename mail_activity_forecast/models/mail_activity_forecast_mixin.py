# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import api, fields, models


class MailActivityForecastMixin(models.AbstractModel):
    _name = 'mail.activity.forecast.mixin'
    _description = 'Activity Forecast Mixin'

    scheduling_activity_id = fields.Many2one(
        comodel_name="mail.activity",
        string="Scheduling Activity",
    )

    @api.model
    def create(self, vals):
        production = super(MailActivityForecastMixin, self).create(vals)
        production._ensure_scheduling_activity()
        production._sync_with_scheduling_activity(vals)
        return production

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if res:
            self._ensure_scheduling_activity()
            self._sync_with_scheduling_activity(vals)
        return res

    @api.multi
    def _get_scheduling_activity_deadline(self):
        self.ensure_one()
        return fields.Date.context_today(self)

    @api.multi
    def _prepare_scheduling_activity_data(self):
        self.ensure_one()
        act_type = self.env.ref("mail_activity_forecast.mail_activity_schedule")
        return {
            'activity_type_id': act_type.id,
            'user_id': self.user_id.id,
        }

    @api.multi
    def _ensure_scheduling_activity(self):
        for rec in self:
            if not rec.scheduling_activity_id:
                activity_data = rec._prepare_scheduling_activity_data()
                if activity_data:
                    rec.scheduling_activity_id = rec.activity_schedule(
                        '', rec._get_scheduling_activity_deadline(),
                        **activity_data
                    )

    @api.multi
    def _sync_with_scheduling_activity(self, vals):
        for rec in self.filtered("scheduling_activity_id").with_context(
            syncing_mail_activity=True
        ):
            if not rec.env.context.get('syncing_' + rec._name, False):
                start, stop = rec._get_forecast_date_fields()
                if start in vals or stop in vals:
                    rec.scheduling_activity_id.write(
                        {
                            'date_start': rec[start],
                            'date_stop': rec[stop],
                        }
                    )

    def _get_forecast_date_fields(self):
        raise NotImplementedError(
            "This method must return a tuple with the names of the `start` "
            "and `stop` fields"
        )
