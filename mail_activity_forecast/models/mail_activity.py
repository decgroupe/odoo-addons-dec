# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2022

from odoo import models, api, fields

import logging

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    duration = fields.Integer('Duration', )
    date_start = fields.Datetime(
        string='Start Date',
        help="Default start date for this Activity.",
    )
    date_stop = fields.Datetime(
        string='End Date',
        help="Default end date for this Activity.",
    )
    activity_plannable = fields.Boolean(
        related='activity_type_id.plannable',
        readonly=True,
    )
    assigned_resource = fields.Char(
        compute="_compute_assigned_resource",
        help="Get the name of the resource assigned to this activity",
    )

    def write(self, vals):
        res = super().write(vals)
        if res:
            self._sync_with_related_object(vals)
            self._sync_with_event(vals)
        return res

    def _sync_with_related_object(self, vals):
        if 'date_start' in vals or 'date_stop' in vals and not self.env.context.get(
            'syncing_mail_activity', False
        ):
            for rec in self:
                rec = rec.with_context({
                    'syncing_' + rec.res_model: True,
                })
                model = rec.env[rec.res_model]
                if hasattr(model, "_get_forecast_date_fields"):
                    start, stop = model._get_forecast_date_fields()
                    related_object_id = rec.env[rec.res_model].browse(
                        rec.res_id
                    )
                    related_object_id.write(
                        {
                            start: rec.date_start,
                            stop: rec.date_stop,
                        }
                    )

    def _sync_with_event(self, vals):
        if 'date_start' in vals or 'date_stop' in vals and not self.env.context.get(
            'syncing_mail_activity', False
        ):
            for rec in self.filtered("calendar_event_id").with_context(
                syncing_calendar_event=True
            ):
                if rec.calendar_event_id.allday:
                    rec.calendar_event_id.write(
                        {
                            'start': rec.date_start,
                            'stop': rec.date_stop,
                        }
                    )
                else:
                    rec.calendar_event_id.write(
                        {
                            'start_datetime': rec.date_start,
                            'stop_datetime': rec.date_stop,
                        }
                    )

    @api.multi
    def _compute_assigned_resource(self):
        for rec in self.filtered('user_id'):
            rec.assigned_resource = rec.user_id.name
