# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2024


from odoo import models, tools


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_compute_author(
        self, author_id=None, email_from=None, raise_exception=True
    ):
        """Reformat email if no name information:
        yanapa@laposte.net -> "yanapa@laposte.net <yanapa@laposte.net>" that way it will
        be displayed "yanapa@laposte.net <notifications@mydomain.com>" instead of
        "notifications@mydomain.com"
        """
        author_id, email_from = super()._message_compute_author(
            author_id, email_from, raise_exception
        )
        # reformat email if no name information
        if not author_id and email_from:
            name_emails = tools.email_split_tuples(email_from)
            name_from_email = name_emails[0][0] if name_emails else False
            if not name_from_email:
                email_from = tools.formataddr((email_from, email_from))

        return author_id, email_from
