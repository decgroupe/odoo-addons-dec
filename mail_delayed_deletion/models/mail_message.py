# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MailMessage(models.AbstractModel):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        res = super(MailMessage, self).create(vals)
        _logger.info("Creating %s", res)
        return res

    def unlink(self):
        for rec in self:
            _logger.info("Deleting %s", rec.message_id)
        return super().unlink()
