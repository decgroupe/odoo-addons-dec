# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2022

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = ["mail.activity", "gantt.task.mixin"]
    _name = "mail.activity"

    def _compute_gantt_assigned_resource(self):
        super()._compute_gantt_assigned_resource()
        for rec in self:
            rec.gantt_assigned_resource = rec.assigned_resource
