# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

import logging
from datetime import date

import lxml
from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def action_snooze(self, unit, value, from_date=None):
        self.ensure_one()
        today = date.today()
        if unit == "d" or unit == "day":
            delta = relativedelta(days=value)
        elif unit == "w" or unit == "week":
            delta = relativedelta(weeks=value)
        elif unit == "m" or unit == "month":
            delta = relativedelta(months=value)
        elif unit == "y" or unit == "year":
            delta = relativedelta(years=value)
        else:
            raise UserError(_("Invalid time unit code"))
        for rec in self:
            if from_date:
                previous_deadline = fields.Date.to_date(from_date)
            else:
                previous_deadline = rec.date_deadline
            if previous_deadline < today:
                date_deadline = today + delta
            else:
                date_deadline = previous_deadline + delta

            notify_txt = _("Deadline extended from %s to %s (by %s)") % (
                format_date(self.env, previous_deadline),
                format_date(self.env, date_deadline),
                self.env.user.name,
            )
            notify_html = "<small><br /> - %s</small>" % (notify_txt)
            root = lxml.html.fromstring(rec.note)
            if (node := root.xpath(".")) and node[0].tag == "p":
                node[0].insert(0, lxml.etree.XML(notify_html))
                note = lxml.etree.tostring(root, pretty_print=False, encoding="UTF-8")
            else:
                note = rec.note + notify_html
            rec.write(
                {
                    "date_deadline": date_deadline,
                    "note": note,
                }
            )
        return True
