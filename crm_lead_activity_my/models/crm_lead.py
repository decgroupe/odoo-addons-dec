# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

import logging

from datetime import date, datetime, timedelta

from odoo import api, models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'mail.activity.my.mixin']

    def action_snooze(self):
        self.ensure_one()
        today = date.today()
        my_next_activity = self.activity_my_ids[:1]
        if my_next_activity:
            delta = timedelta(days=7)
            if my_next_activity.date_deadline < today:
                date_deadline = today + delta
            else:
                date_deadline = my_next_activity.date_deadline + delta
            my_next_activity.write({'date_deadline': date_deadline})
        return True
