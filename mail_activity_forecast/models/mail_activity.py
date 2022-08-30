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

    def unlink(self):
        _logger.info("🗑️ Deleting %s", self)
        return super().unlink()

    def _sync_with_related_object(self, vals):
        if 'date_start' in vals or 'date_stop' in vals \
        or 'date_deadline' in vals and not self.env.context.get(
            'syncing_mail_activity', False
        ):
            for rec in self:
                context_name = 'syncing_' + rec.res_model.replace('.', '_')
                rec = rec.with_context({context_name: True})
                model = rec.env[rec.res_model]
                if hasattr(model, "_get_forecast_date_fields"):
                    data = {}
                    date_fields = model._get_forecast_date_fields()
                    if date_fields.get('start') and 'date_start' in vals:
                        data[date_fields['start']] = rec.date_start
                    if date_fields.get('stop') and 'date_stop' in vals:
                        data[date_fields['stop']] = rec.date_stop
                    if date_fields.get('deadline') and 'date_deadline' in vals:
                        data[date_fields['deadline']] = rec.date_deadline
                    if data:
                        related_object_id = rec.env[rec.res_model].browse(
                            rec.res_id
                        )
                        related_object_id.with_context(tracking_disable=True,
                                                      ).write(data)

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
