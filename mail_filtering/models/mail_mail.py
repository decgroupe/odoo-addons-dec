# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

import logging

from odoo import api, models
from odoo.tools import ormcache
from odoo.tools.config import config, to_list

_logger = logging.getLogger(__name__)


class MailMail(models.AbstractModel):
    _inherit = "mail.mail"

    @api.model
    @ormcache()
    def _get_db_process_email_allowedlist(self):
        """Return the list of databases allowed to send emails from config."""
        res = []
        allowedlist = config.get("db_process_email_allowedlist")
        if allowedlist:
            res = to_list(allowedlist)
        return res

    @api.model
    def process_email_queue(self, ids=None):
        """Override to raise if sending is not allowed for the current database."""
        return super(
            MailMail, self.with_context(raise_if_send_not_allowed=True)
        ).process_email_queue(ids)

    def _send(
        self,
        auto_commit=False,
        raise_exception=False,
        smtp_session=None,
        alias_domain_id=False,
        mail_server=False,
        post_send_callback=None,
    ):
        """Override to filter outgoing emails based on allowed_databases field."""
        # determine which mail server is being used for this batch
        if not mail_server and hasattr(smtp_session, "mail_server_id"):
            mail_server = (
                self.env["ir.mail_server"].sudo().browse(smtp_session.mail_server_id)
            )
        send_allowed = False
        if mail_server and mail_server.allowed_databases:
            if mail_server.allowed_databases == "*":
                send_allowed = True
            else:
                send_allowed = self.env.cr.dbname in to_list(
                    mail_server.allowed_databases
                )
        if not send_allowed:
            send_allowed = (
                self.env.cr.dbname in self._get_db_process_email_allowedlist()
            )
        if send_allowed:
            return super()._send(
                auto_commit,
                raise_exception,
                smtp_session,
                alias_domain_id,
                mail_server,
                post_send_callback,
            )
        _logger.info(
            "_send disabled for %s", mail_server.name if mail_server else "unknown"
        )
        if self.env.context.get("raise_if_send_not_allowed"):
            raise Exception(
                "Sending with %s is not allowed"
                % (mail_server.name if mail_server else "unknown")
            )
        return False
