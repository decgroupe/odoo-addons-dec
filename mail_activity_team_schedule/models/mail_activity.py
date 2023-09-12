# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def _compute_assigned_resource(self):
        super()._compute_assigned_resource()
        for rec in self.filtered("team_id"):
            if not rec.assigned_resource:
                rec.assigned_resource = rec.team_id.name
