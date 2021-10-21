# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import logging

from datetime import datetime, timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MailMail(models.AbstractModel):
    _inherit = 'mail.mail'

    delayed_deletion = fields.Datetime(
        string='Delayed Deletion',
        help="When « auto_delete » is set, it will occured at the specified "
        "date/time",
    )

    def _get_delayed_deletion_days(self):
        ICP = self.env['ir.config_parameter'].sudo()
        delayed_deletion_days = int(ICP.get_param('mail_delayed_deletion.days'))
        return delayed_deletion_days

    @api.multi
    def _send(
        self,
        auto_commit=False,
        raise_exception=False,
        smtp_session=None,
    ):
        delayed_deletion_days = self._get_delayed_deletion_days()
        if delayed_deletion_days:
            mail_ids = self.browse(self.ids).filtered('auto_delete')
            if mail_ids:
                mail_ids.write(
                    {
                        'auto_delete':
                            False,
                        'delayed_deletion':
                            datetime.today() +
                            timedelta(days=delayed_deletion_days)
                    }
                )
        return super()._send(auto_commit, raise_exception, smtp_session)

    @api.model
    def action_delayed_deletion(self):
        domain = [
            ('delayed_deletion', '<=', datetime.today()),
        ]
        mail_ids = self.search(domain)
        if mail_ids:
            mail_ids.unlink()
