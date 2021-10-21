# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

import logging

from odoo import api, models, _
from odoo.tools import ormcache
from odoo.tools.config import config, to_list

_logger = logging.getLogger(__name__)


class MailMail(models.AbstractModel):
    _inherit = 'mail.mail'

    @api.model
    @ormcache()
    def _get_db_process_email_allowedlist(self):
        res = []
        allowedlist = config.get("db_process_email_allowedlist")
        if allowedlist:
            res = to_list(allowedlist)
        return res

    # @api.multi
    # def _split_by_server(self):
    #     self.env.context = {}
    #     for server_id, mail_batch in super()._split_by_server():
    #         # Use dirty context hook to pass mail server data
    #         self.env.context.update({'mail_server_id': server_id})
    #         yield server_id, mail_batch

    @api.model
    def process_email_queue(self, ids=None):
        return super(
            MailMail, self.with_context(raise_if_send_not_allowed=True)
        ).process_email_queue(ids)

    @api.multi
    def _send(
        self,
        auto_commit=False,
        raise_exception=False,
        smtp_session=None,
    ):
        mail_server_id = self.env["ir.mail_server"].sudo()
        # Get the mail server used to create the `smtp_session`
        if hasattr(smtp_session, 'mail_server_id'):
            mail_server_id = mail_server_id.browse(smtp_session.mail_server_id)

        # if self.env.context.get('mail_server_id'):
        #     mail_server_id = self.env["ir.mail_server"].browse(
        #         self.env.context.get('mail_server_id')
        #     )
        # else:
        #     # Use default server like odoo/addons/base/models/ir_mail_server.py
        #     mail_server_id = self.env["ir.mail_server"].sudo().search(
        #         [], order='sequence', limit=1
        #     )

        send_allowed = False
        if mail_server_id.allowed_databases:
            if mail_server_id.allowed_databases == '*':
                send_allowed = True
            else:
                send_allowed = self.env.cr.dbname in to_list(
                    mail_server_id.allowed_databases
                )

        if not send_allowed:
            send_allowed = self.env.cr.dbname in \
                self._get_db_process_email_allowedlist()

        if send_allowed:
            return super()._send(auto_commit, raise_exception, smtp_session)
        else:
            _logger.info('_send disabled for %s', mail_server_id.name)
            if self.env.context.get('raise_if_send_not_allowed'):
                raise Exception(
                    'Sending with %s is not allowed' % (mail_server_id.name)
                )
            return False
