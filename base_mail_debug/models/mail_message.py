# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

import logging
import tempfile

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailMessage(models.AbstractModel):
    _inherit = "mail.message"

    def _ensure_create_values(self, vals_list):
        """When filling default values, upstream will check for existing key in values
        dictionary, but don't care if this value exists and is False. The purpose of
        this function is to delete False values from the dictionary to ensure valid
        default values will be filled by ./odoo/addons/mail/models/mail_message.py
        """
        for values in vals_list:
            if "email_from" in values and not values["email_from"]:
                values.pop("email_from")
                _logger.info("Empty field 'email_from' dropped")
            if "reply_to" in values and not values["reply_to"]:
                values.pop("reply_to")
                _logger.info("Empty field 'reply_to' dropped")

    @api.model_create_multi
    def create(self, vals_list):
        self._ensure_create_values(vals_list)
        record_ids = super().create(vals_list)
        for rec, vals in zip(record_ids, vals_list, strict=True):
            # generate a random filename
            if vals.get("body"):
                prefix = None
                message_id = vals.get("message_id") or rec.message_id
                if message_id:
                    prefix = message_id.replace("<", "").replace(">", "") + "_"
                tf = tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    delete=False,
                    # delete_on_close=False,
                    prefix=prefix,
                    suffix=".html",
                )
                tf.write(vals.get("body"))
                body_filename = tf.name
                tf.close()
            else:
                body_filename = "<empty>"

            _logger.info(
                "📧 New mail.message\n"
                "          Message-Id: %r\n"
                "        Message Type: %s\n"
                "            Reply-To: %s\n"
                "                From: %s\n"
                "              Author: %s\n"
                "                  To: %s\n"
                "             Subject: %s\n"
                "              Layout: %s\n"
                "           Signature: %s\n"
                "                Body: %s\n"
                "       Activity Type: %s\n"
                "               Model: %s\n"
                "         Record Name: %s\n"
                "      Record Company: %s\n"
                " Record Alias Domain: %s\n",
                rec.message_id,
                rec.message_type,
                rec.reply_to,
                rec.email_from,
                rec.author_id.display_name,
                rec.partner_ids.mapped("email"),
                rec.subject,
                rec.email_layout_xmlid,
                rec.email_add_signature,
                body_filename,
                rec.mail_activity_type_id.display_name,
                rec.model,
                rec.record_name,
                rec.record_company_id.display_name,
                rec.record_alias_domain_id.display_name,
            )
        return record_ids
