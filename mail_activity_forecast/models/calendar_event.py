# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2022

from pytz import timezone, utc
from odoo import _, api, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def write(self, vals):
        res = super().write(vals)
        if res:
            self._sync_with_activities(vals)
        return res

    def _sync_with_activities(self, vals):
        if self.activity_ids and (
            'start' in vals or 'stop' in vals
        ) and not self.env.context.get('syncing_calendar_event', False):
            rec = self.with_context(syncing_mail_activity=True)
            if self.allday:
                # We don't use `start_date` nor `stop_date` to have a
                # better precision for gantt view. But `start` and `stop`
                # are set in user timezone, so we need to convert them
                # to UTC first
                def _localize_datetime(dt):
                    tz = timezone(self.env.user.tz)
                    if tz and not dt.tzinfo:
                        res = tz.localize(dt).astimezone(utc)
                    else:
                        res = dt
                    return res

                start = rec.start
                stop = rec.stop.replace(hour=23, minute=59, second=59)

                start = _localize_datetime(start)
                stop = _localize_datetime(stop)

                rec.activity_ids.write(
                    {
                        'date_start': start,
                        'date_stop': stop,
                    }
                )
            else:
                rec.activity_ids.write(
                    {
                        'date_start': rec.start_datetime,
                        'date_stop': rec.stop_datetime,
                    }
                )