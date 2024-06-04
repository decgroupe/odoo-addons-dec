# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

import email.message
import email.policy
import logging
from unittest.mock import patch

from odoo.addons.base.models.ir_mail_server import IrMailServer
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase

_test_logger = logging.getLogger("odoo.tests")

class TestBaseMailAutoCopyCommon(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Mail = self.env["mail.mail"]
        # disable all active mail servers
        self._disable_all_servers()
        # create test servers
        self.primary_mail_server = self.env["ir.mail_server"].create(
            {
                "name": "OutgoingMailServer#1",
                "smtp_host": "localhost",
                "sequence": 1,
            }
        )
        self.secondary_mail_server = self.env["ir.mail_server"].create(
            {
                "name": "OutgoingMailServer#2",
                "smtp_host": "localhost",
                "sequence": 2,
            }
        )
        self.MESSAGE_ID = "123456789"

    def _disable_all_servers(self):
        """Disable all active mail servers"""
        self.env["ir.mail_server"].search([]).write({"active": False})

    def _get_mail_server(self, auto_add_sender=True):
        mail_server = self.env["ir.mail_server"].get_mail_server(
            mail_server_id=False, smtp_server=False
        )
        if mail_server:
            mail_server.auto_add_sender = auto_add_sender
        return mail_server

    def _send_email(self, msg, check_fn):
        send_email_origin = IrMailServer.send_email

        def _ir_mail_server_send_email(model, message, *args, **kwargs):
            check_fn(message)
            return send_email_origin(model, message, *args, **kwargs)

        # patch `send_mail` to check content
        with patch.object(
            IrMailServer,
            "send_email",
            autospec=True,
            wraps=IrMailServer,
            side_effect=_ir_mail_server_send_email,
        ) as ir_mail_server_send_email_mock:
            res = self.env["ir.mail_server"].send_email(msg)
        return res

    def _create_user(self, login):
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        user = new_test_user(
            self.env,
            login=login,
            groups="base.group_user",
            context=ctx,
        )
        return user

    def _join_channel(self, channel, partners):
        for partner in partners:
            channel.write(
                {"channel_last_seen_partner_ids": [(0, 0, {"partner_id": partner.id})]}
            )
        channel.invalidate_cache()

    def _get_message_from_john_to_jane(self):
        msg = email.message.EmailMessage(policy=email.policy.SMTP)
        msg["From"] = '"John Doe" <john@example.com>'
        msg["To"] = '"Jane Doe" <jane@example.com>'
        msg["Message-Id"] = self.MESSAGE_ID
        return msg

    def _mail_unlink_disabled(self):
        # disable automatic mail-deletion
        def unlink(self):
            _test_logger.warning("Unlink disabled for `mail.mail`")

        self.Mail._patch_method("unlink", unlink)

    def _mail_unlink_enabled(self):
        # restore original method
        self.Mail._revert_method("unlink")

    def _build_email_from_mail(self, mail_id, to=False):
        message = self.env["ir.mail_server"].build_email(
            email_from=mail_id.email_from,
            email_to=mail_id.email_to or to,
            subject=mail_id.subject,
            body=mail_id.body,
            reply_to=mail_id.reply_to,
            references=mail_id.references,
            message_id=mail_id.message_id,
            subtype="html",
            subtype_alternative="plain",
        )
        return message

MSG_CONTACT = """Return-Path: xyz@widget.com
Delivered-To: catchall@yourcompany.com
Received: from [127.0.0.1] (localhost [127.0.0.1]) by localhost (Mailerdaemon) with ESMTPSA id F274EC009F
    for <contact@yourcompany.com>; Mon, 22 Apr 2024 15:39:19 +0200 (CEST)
Message-ID: <58976bdf-e97b-4c3a-a103-2888d10615fd@widget.com>
Date: Mon, 22 Apr 2024 15:39:19 +0200
MIME-Version: 1.0
User-Agent: Mozilla Thunderbird
Content-Language: en-US
To: contact@yourcompany.com
From: "Xan Yin Zu (myhostname)" <xyz@widget.com>
Subject: Need information about your products
Content-Type: text/plain; charset=UTF-8; format=flowed
Content-Transfer-Encoding: 7bit
X-Last-TLS-Session-Version: TLSv1.3

I need details about all your software.

Can you contact me at xyz@widget.com ?

Thank you

"""
