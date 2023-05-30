# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

import logging

from odoo import api, fields, models, _
from odoo.tools import ormcache
from odoo.tools.config import config, to_list

_logger = logging.getLogger(__name__)


class FetchmailServer(models.AbstractModel):
    _inherit = "fetchmail.server"

    allowed_databases = fields.Char(
        string="Allowed Databases",
        default="*",
        help="Comma-separated list of database names allowed to send "
        "e-mails with this server, or set it to «*» to allow all.",
    )

    @api.model
    @ormcache()
    def _get_db_fetchmail_allowedlist(self):
        res = []
        allowedlist = config.get("db_fetchmail_allowedlist")
        if allowedlist:
            res = to_list(allowedlist)
        return res

    def fetch_mail(self):
        # We use `fetch_mail` instead of `_fetch_mails`
        fetchmail_server_ids = self.env["fetchmail.server"]

        for fetchmail_server_id in self:
            fetch_allowed = False
            if fetchmail_server_id.allowed_databases:
                if fetchmail_server_id.allowed_databases == "*":
                    fetch_allowed = True
                else:
                    fetch_allowed = self.env.cr.dbname in to_list(
                        fetchmail_server_id.allowed_databases
                    )

            if not fetch_allowed:
                fetch_allowed = (
                    self.env.cr.dbname in self._get_db_fetchmail_allowedlist()
                )

            if fetch_allowed:
                fetchmail_server_ids += fetchmail_server_id
            else:
                _logger.info("fetch_mail disabled for %s", fetchmail_server_id.name)

        return super(FetchmailServer, fetchmail_server_ids).fetch_mail()
