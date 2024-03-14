# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

import logging

from odoo import api, fields, models
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    auto_add_sender = fields.Boolean(
        string="Auto add sender",
        help="Automatically add sender to the list of hidden recipients",
    )
    auto_cc_addresses = fields.Text(
        string="Auto CC addresses",
        help="Comma-separated list of auto Cc addresses",
    )
    auto_bcc_addresses = fields.Text(
        string="Auto BCC addresses",
        help="Comma-separated list of auto Bcc addresses",
    )

    def _get_mail_message(self, message):
        message_id = self.env["mail.message"].search(
            [("message_id", "=", message.get("message-id"))],
            order="id desc",
            limit=1,
        )
        return message_id

    def get_mail_server(self, mail_server_id, smtp_server):
        # Get mail_server like it's done in
        # addons/base/models/ir_mail_server.py
        if mail_server_id:
            mail_server = self.sudo().browse(mail_server_id)
        elif not smtp_server:
            mail_server = self.sudo().search([], order="sequence", limit=1)
        else:
            mail_server = False
        return mail_server

    def update_cc_addresses(self, mail_server, message):
        if mail_server.auto_cc_addresses:
            if not message.get("Cc"):
                message["Cc"] = mail_server.auto_cc_addresses
            else:
                del message["Cc"]  # avoid multiple Cc: headers!
                message["Cc"] += "," + mail_server.auto_cc_addresses

    def update_bcc_addresses(self, mail_server, message):
        auto_bcc_addresses = mail_server.auto_bcc_addresses

        if mail_server.auto_add_sender:
            # retrieve original message
            mail_message_id = self._get_mail_message(message)
            ignore_auto_add_sender = False
            from_rfc2822 = extract_rfc2822_addresses(message["From"])
            if mail_message_id.model == "mail.channel":
                # Do not automatically add sender to bcc if the message comes
                # from a channel
                channel_email_from_rfc2822 = extract_rfc2822_addresses(
                    mail_message_id.email_from
                )
                if from_rfc2822[0] == channel_email_from_rfc2822[0]:
                    _logger.info("Do not add %s to BCC - R1", from_rfc2822[0])
                    ignore_auto_add_sender = True
            if not ignore_auto_add_sender:
                partner_id = self.env["res.partner"].search(
                    [("email", "=", from_rfc2822[0])], limit=1
                )
                if partner_id and not partner_id.copy_sent_email:
                    _logger.info("Do not add %s to BCC - R2", from_rfc2822[0])
                    ignore_auto_add_sender = True
            if not ignore_auto_add_sender:
                if not auto_bcc_addresses:
                    auto_bcc_addresses = message["From"]
                else:
                    auto_bcc_addresses += "," + message["From"]

        if auto_bcc_addresses:
            _logger.info(
                "Message-Id %r BCC to %s", message.get("message-id"), auto_bcc_addresses
            )
            if not message.get("Bcc"):
                message["Bcc"] = auto_bcc_addresses
            else:
                del message["Bcc"]  # avoid multiple Bcc: headers!
                message["Bcc"] += "," + auto_bcc_addresses

    @api.model
    def send_email(
        self,
        message,
        mail_server_id=None,
        smtp_server=None,
        smtp_port=None,
        smtp_user=None,
        smtp_password=None,
        smtp_encryption=None,
        smtp_debug=False,
        smtp_session=None,
    ):
        mail_server = self.get_mail_server(mail_server_id, smtp_server)
        if mail_server:
            self.update_cc_addresses(mail_server, message)
            self.update_bcc_addresses(mail_server, message)

        message_id = super(IrMailServer, self).send_email(
            message,
            mail_server_id=mail_server_id,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            smtp_encryption=smtp_encryption,
            smtp_debug=smtp_debug,
            smtp_session=smtp_session,
        )
        return message_id
