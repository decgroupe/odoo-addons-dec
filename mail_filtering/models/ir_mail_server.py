# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

import logging

from odoo import fields, models, modules

logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    allowed_databases = fields.Char(
        string="Allowed Databases",
        default="*",
        help="Comma-separated list of database names allowed to send "
        "e-mails with this server, or set it to «*» to allow all.",
    )

    def connect(
        self,
        host=None,
        port=None,
        user=None,
        password=None,
        encryption=None,
        smtp_from=None,
        ssl_certificate=None,
        ssl_private_key=None,
        smtp_debug=False,
        mail_server_id=None,
        allow_archived=False,
    ):
        # Use default server like odoo/addons/base/models/ir_mail_server.py
        mail_server = self.sudo()
        if mail_server_id:
            mail_server = mail_server.browse(mail_server_id)
        elif not host:
            mail_server, _smtp_from = self.sudo()._find_mail_server(smtp_from)

        connection = super().connect(
            host=host,
            port=port,
            user=user,
            password=password,
            encryption=encryption,
            smtp_from=smtp_from,
            ssl_certificate=ssl_certificate,
            ssl_private_key=ssl_private_key,
            smtp_debug=smtp_debug,
            mail_server_id=mail_server_id,
            allow_archived=allow_archived,
        )
        # Keep a track of the smtp server used to create the `smtp_session`
        if mail_server:
            if not connection and modules.module.current_test:
                logger.warning(
                    "No connection returned for mail server %s because of a "
                    "mocked SMTP server in test mode",
                    mail_server.name,
                )
            else:
                connection.mail_server_id = mail_server.id
        return connection
