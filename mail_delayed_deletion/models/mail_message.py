# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailMessage(models.AbstractModel):
    _inherit = "mail.message"

    @api.model
    def create(self, vals):
        res = super(MailMessage, self).create(vals)
        name = "%s (%s)" % (res.message_id, res.subject)
        _logger.info("💬 Creating %s", name)
        return res

    def unlink(self):
        for rec in self:
            name = "%s (%s)" % (rec.message_id, rec.subject)
            _logger.info("💬 Deleting %s", name)
        return super().unlink()
