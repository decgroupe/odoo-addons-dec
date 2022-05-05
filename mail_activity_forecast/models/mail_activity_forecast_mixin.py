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
        rec = super(MailActivityForecastMixin, self).create(vals)
        rec._ensure_scheduling_activity()
        rec._sync_with_scheduling_activity(vals)
        return rec

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
        res = fields.Date.context_today(self)
        date_fields = self._get_forecast_date_fields()
        if date_fields.get('deadline'):
            res = self[date_fields['deadline']] or res
        return res

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
        if 'mail.activity.mixin' not in self._inherit_module:
            return
        for rec in self:
            if not rec.scheduling_activity_id:
                activity_data = rec._prepare_scheduling_activity_data()
                if activity_data:
                    rec.scheduling_activity_id = rec.activity_schedule(
                        '', rec._get_scheduling_activity_deadline(),
                        **activity_data
                    )
                    rec._sync_with_scheduling_activity(vals=False)

    @api.multi
    def _sync_with_scheduling_activity(self, vals=False):
        if 'mail.activity.mixin' not in self._inherit_module:
            return
        for rec in self.filtered("scheduling_activity_id").with_context(
            syncing_mail_activity=True
        ):
            context_name = 'syncing_' + rec._name.replace('.', '_')
            if not rec.env.context.get(context_name, False):
                data = {}
                date_fields = rec._get_forecast_date_fields()
                if not vals or date_fields['start'] in vals:
                    data['date_start'] = rec[date_fields['start']]
                if not vals or date_fields['stop'] in vals:
                    data['date_stop'] = rec[date_fields['stop']]
                if not vals or date_fields['deadline'] in vals:
                    data['date_deadline'
                        ] = rec._get_scheduling_activity_deadline()
                if data:
                    rec.scheduling_activity_id.write(data)

    def _get_forecast_date_fields(self):
        return {
            'start': False,
            'stop': False,
            'deadline': False,
        }
