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

    def write(self, vals):
        res = super().write(vals)
        if res:
            self._sync_with_event(vals)
        return res


    def _sync_with_event(self, vals):
        if self.calendar_event_id and not self.env.context.get(
            'syncing_mail_activity', False
        ):
            rec = self.with_context(syncing_calendar_event=True)
            if 'date_start' in vals or 'date_stop' in vals:
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