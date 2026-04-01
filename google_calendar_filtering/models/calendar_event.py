# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2024

import logging

from odoo import api, fields, models
from odoo.tools.progressbar import progressbar as pb

from odoo.addons.google_calendar.utils.google_calendar import (
    GoogleCalendarService,
)

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    duplicate_count = fields.Integer(
        string="Duplicate's Count",
        compute="_compute_duplicate_count",
        store=True,
    )

    @api.model
    def _get_public_fields(self):
        """Extend public fields to include duplicate_count."""
        return super()._get_public_fields() | {"duplicate_count"}

    @api.depends("start", "stop", "start_date", "stop_date", "allday", "name")
    def _compute_duplicate_count(self):
        """Compute the number of duplicate events based on name and date."""
        self.action_recompute_duplicate_count()

    def action_recompute_duplicate_count(self):
        """Recompute duplicate_count for the current recordset.
        When called during module installation, resets all counts to 0.
        """
        if self.env.context.get("module") == "google_calendar_filtering":
            self.write({"duplicate_count": 0})
        else:
            done = []
            for rec in pb(self.sorted(key=lambda r: r.id)):
                if rec.id in done:
                    continue
                domain = [
                    ("id", ">", rec.id),
                    ("name", "=", rec.name),
                    ("allday", "=", rec.allday),
                ]
                if rec.allday:
                    domain.extend(
                        [
                            ("start_date", "=", rec.start_date),
                            ("stop_date", "=", rec.stop_date),
                        ]
                    )
                else:
                    domain.extend(
                        [
                            ("start", "=", rec.start),
                            ("stop", "=", rec.stop),
                        ]
                    )
                res = self.with_context(active_test=False).search(domain)
                if res:
                    (res + rec).write({"duplicate_count": len(res)})
                    done.extend(res.ids)
                else:
                    rec.duplicate_count = 0
                done.append(rec.id)
        return None

    def action_sync2google(self):
        """Manually push the selected events to Google Calendar."""
        calendar_service = GoogleCalendarService(self.env["google.service"])

        # Odoo -> Google
        for rec in self:
            user = rec.user_id
            full_sync = not bool(user.google_calendar_sync_token)
            # with google_calendar_token(user) as token:
            #     try:
            #         events, next_sync_token, default_reminders = (
            #             calendar_service.get_events(
            #                 user.google_calendar_sync_token, token=token
            #             )
            #         )
            #     except InvalidSyncToken:
            #         events, next_sync_token, default_reminders = (
            #             calendar_service.get_events(token=token)
            #         )
            #         full_sync = True
            # user.google_calendar_sync_token = next_sync_token

            if full_sync:
                raise ValueError("We don't want full sync")

            if (not rec.google_id and rec.active) or rec.need_sync:
                rec.with_context(send_updates=False)._sync_odoo2google(calendar_service)
