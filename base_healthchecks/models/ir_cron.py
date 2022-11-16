# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2022

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = "ir.cron"

    @api.model
    def _callback(self, cron_name, server_action_id, job_id):
        return super(IrCron, self.with_context(
            cron_running=True
        ))._callback(cron_name, server_action_id, job_id)
