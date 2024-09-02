# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date
import lxml

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def action_snooze(self, unit, value):
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
            raise UserError(_("Invalid unit code"))
        for rec in self:
            previous_deadline = rec.date_deadline
            if rec.date_deadline < today:
                date_deadline = today + delta
            else:
                date_deadline = rec.date_deadline + delta

            notify_txt = "<small><br /> - Deadline extended from %s" % format_date(
                self.env, previous_deadline
            )
            root = lxml.html.fromstring(rec.note)
            if (node := root.xpath(".")) and node[0].tag == "p":
                node[0].insert(0, lxml.etree.XML(notify_txt))
                note = lxml.etree.tostring(root, pretty_print=False, encoding="UTF-8")
            else:
                note += notify_txt
            rec.write(
                {
                    "date_deadline": date_deadline,
                    "note": note,
                }
            )
        return True
