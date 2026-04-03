# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailMessage(models.AbstractModel):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, vals_list):
        """Create message records and log their creation."""
        records = super().create(vals_list)
        for res in records:
            name = f"{res.message_id} ({res.subject})"
            _logger.info("💬 Creating %s", name)
        return records

    def unlink(self):
        """Log deletion details before removing message records."""
        for rec in self:
            name = f"{rec.message_id} ({rec.subject})"
            _logger.info("💬 Deleting %s", name)
        return super().unlink()
