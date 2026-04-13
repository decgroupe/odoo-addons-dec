# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026


import json
import logging

from werkzeug import urls

from odoo import models, tools
from odoo.exceptions import UserError
from odoo.tools.mail import append_content_to_html, email_normalize

from odoo.addons.mail_group.models.mail_group import GROUP_SEND_BATCH_SIZE

_logger = logging.getLogger(__name__)


class MailGroup(models.Model):
    _inherit = "mail.group"

    # ------------------------------------------------------------
    # MAILING
    # ------------------------------------------------------------

    def _get_notify_headers(
        self, message, base_url, email_url_encoded, unsubscribe_url
    ):
        headers = {
            **self._notify_by_email_get_headers(),
            "List-Archive": f"<{base_url}/groups/{self.env['ir.http']._slug(self)}>",
            "List-Subscribe": f"<{base_url}/groups?email={email_url_encoded}>",
            "List-Unsubscribe": f"<{unsubscribe_url}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            "Precedence": "list",
            "X-Auto-Response-Suppress": "OOF",  # avoid out-of-office replies from MS Exchange  # noqa: E501
        }
        if self.alias_email:
            headers.update(
                {
                    "List-Id": f"<{self.alias_email}>",
                    "List-Post": f"<mailto:{self.alias_email}>",
                    "X-Forge-To": f'"{self.name}" <{self.alias_email}>',
                }
            )

        if message.mail_message_id.parent_id:
            headers["In-Reply-To"] = message.mail_message_id.parent_id.message_id

        return headers

    def _notify_get_recipients(self):
        # prefetch members data for qweb rendering
        res = self.env["mail.group.member"]._get_recipient_data(self)
        return list(res[self.id].values())

    def _notify_get_recipients_classify(self, message, recipients_data):
        """Classify recipients to be notified of a message in groups to have
        specific rendering depending on their group.
        This function mimic the `_notify_get_recipients_classify` of `mail.thread` but
        is adapted to mail groups and their members.
        Note that we still call original `_notify_get_recipients_groups` to get the
        groups.
        WARNING: Contrary to original method, recipients are not `res.partner` but
        `mail.group.member`.
        """
        model_description = False
        local_msg_vals = {}
        groups = self.env["mail.thread"]._notify_get_recipients_groups_fillup(
            self.env["mail.thread"]._notify_get_recipients_groups(
                message, model_description=False, msg_vals=local_msg_vals
            ),
            model_description=model_description,
            msg_vals=local_msg_vals,
        )
        # enable "portal" group that is normally set active per model
        portal_group = next((group for group in groups if group[0] == "portal"), None)
        if portal_group:
            portal_group[2]["active"] = True
        # classify recipients in each group
        for recipient_data in recipients_data:
            for _group_name, group_func, group_data in groups:
                _logger.info("Check group mapping against %r", _group_name)
                if group_data["active"] and group_func(recipient_data):
                    member_id = (
                        self.env["mail.group.member"]
                        .sudo()
                        .browse(recipient_data["id"])
                    )
                    _logger.info(
                        "- %s (%s) added to group %r",
                        member_id,
                        member_id.display_name,
                        _group_name,
                    )
                    group_data["recipients"].append(recipient_data["id"])
                    break
        # filter out groups without recipients
        res = [
            group_data
            for _group_name, _group_func, group_data in groups
            if group_data["recipients"]
        ]
        # like `mail_qweb` override
        for group_data in res:
            recipient_ids = group_data["recipients"]
            group_data["_origin"] = "mail_group_qweb"
            group_data["_members"] = self.env["mail.group.member"].browse(recipient_ids)
            group_data["_members_notif_mode"] = {}
            for r in recipients_data:
                if r["id"] in recipient_ids:
                    group_data["_members_notif_mode"][r["id"]] = r["notif"]
        return res

    def _notify_by_email_prepare_rendering_context(
        self, message, recipients_groups_data, member
    ):
        """Prepare the qweb rendering context for the mail group notification.
        This method is called in `_notify_thread_by_email` to prepare the context
        before rendering the email body. It allows to add specific values in the
        context that can be used in the qweb template.

        WARNING: This function mimic the `_notify_by_email_prepare_rendering_context`
        of `mail.thread` but a lot of values are missing like:
            is_discussion, subtype, tracking_values, model_description, record,
            record_name, subtitles, author_user, company, email_add_signature, lang,
            signature, website_url, is_html_empty, email_notification_force_header,
            email_notification_force_footer, email_notification_allow_header,
            email_notification_allow_footer, etc.
        """
        Mailthread = self.env["mail.thread"]
        # re-use auto-align of `mail_qweb` for better rendering of the message body in
        # the email
        align = Mailthread._get_notify_content_message_align(message)
        # extract group name for current member
        group_name = None
        for recipients_group in recipients_groups_data:
            if member.id in recipients_group["recipients"]:
                group_name = recipients_group["notification_group_name"]
                break
        # add values in the context that can be used in the qweb template
        render_values = {
            # minimum record for the template (include body, subject, etc.)
            "message": message,
            "recipients_groups_data": recipients_groups_data,
            "notification_group_name": group_name,
            "content_message_align": align,
        }
        return render_values

    def _notify_members(self, message):
        """Send the given message to all members of the mail group (except the author).
        WARNING: This method override the default mail group notification.
        """
        self.ensure_one()

        if message.mail_group_id != self:
            raise UserError(self.env._("The group of the message do not match."))

        if not message.mail_message_id.reply_to:
            _logger.error(
                "The alias or the catchall domain is missing, "
                "group might not work properly."
            )

        base_url = self.get_base_url()
        body = self.env["mail.render.mixin"]._replace_local_links(message.body)

        partners_data = self._notify_get_recipients()
        recipients_groups_data = self._notify_get_recipients_classify(
            message, partners_data
        )

        # Email added in a dict to be sure to send only once the email to each address
        members = {email_normalize(member.email): member for member in self.member_ids}

        batch_size = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mail.session.batch.size", GROUP_SEND_BATCH_SIZE)
        )
        for batch_member in tools.split_every(batch_size, members.items()):
            mail_values = []
            for email_member_normalized, member in batch_member:
                if email_member_normalized == message.email_from_normalized:
                    # Do not send the email to their author
                    continue

                template_ctx = self._notify_by_email_prepare_rendering_context(
                    message, recipients_groups_data, member
                )
                body = self.env["ir.qweb"]._render(
                    "mail.mail_notification_light",
                    template_ctx,
                    minimal_qcontext=True,
                    raise_if_not_found=False,
                )

                # SMTP headers related to the subscription
                email_url_encoded = urls.url_quote(member.email)
                unsubscribe_url = self._get_email_unsubscribe_url(
                    email_member_normalized
                )
                headers = self._get_notify_headers(
                    message, base_url, email_url_encoded, unsubscribe_url
                )

                # Add the footer (member specific) in the body
                vals = self._get_footer_vals(base_url, unsubscribe_url)
                footer = self._get_footer(vals)
                member_body = append_content_to_html(body, footer, plaintext=False)

                mail_values.append(
                    {
                        "auto_delete": True,
                        "attachment_ids": message.attachment_ids.ids,
                        "body_html": member_body,
                        "email_from": message.email_from,
                        "email_to": member.email,
                        "headers": json.dumps(headers),
                        "mail_message_id": message.mail_message_id.id,
                        "message_id": message.mail_message_id.message_id,
                        "model": "mail.group",
                        "reply_to": message.mail_message_id.reply_to,
                        "res_id": self.id,
                        "subject": message.subject,
                    }
                )

            if mail_values:
                self.env["mail.mail"].sudo().create(mail_values)

    def _get_footer_vals(self, base_url, unsubscribe_url):
        # Note: there is now shortcut for full email (alias name+domain) => alias_email
        return {
            "maillist": self.env._("Mailing-List"),
            "post_to": self.env._("Post to"),
            "unsub": self.env._("Unsubscribe"),
            "mailto_url": f"mailto:{self.alias_email}",
            "group_url": f"{base_url}/groups/{self.env['ir.http']._slug(self)}",
            "unsub_url": unsubscribe_url,
            "unsub_label": self.env._("Unsubscribe"),
            "group": self.name,
            "group_mail": f"{self.alias_email}",
        }

    def _get_footer(self, vals):
        # fully replace `mail_group.mail_group_footer` default template
        footer = self.env["ir.qweb"]._render(
            "mail_group_qweb.mail_group_footer",
            vals,
            minimal_qcontext=True,
        )
        return footer
