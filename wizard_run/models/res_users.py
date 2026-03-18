# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging
import string
from random import choice

from odoo import fields, models
from odoo.tools import plaintext2html

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def generate_random_signature(self):
        """Generate random string for signature for all users."""
        for user in self:
            random_header = "".join(
                choice(string.ascii_uppercase + string.digits) for _ in range(32)
            )
            text = (
                "This signature was generated randomly by module `wizard_run` for "
                f"user {user.name} ({user.login}) and is not meant to be used in "
                "production."
            )
            date_and_time = (
                "```"
                + f"Generated on {fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                + "```"
            )
            signature = "\n".join([random_header, text, date_and_time])
            _logger.info(
                "Generated random signature for user %s (%s):\n%s",
                user.name,
                user.login,
                signature,
            )
            user.signature = plaintext2html(signature)
