# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging

import lxml

from odoo import models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    # was named `_notify_get_groups` in Odoo 14.0
    def _notify_get_recipients_groups(self, message, model_description, msg_vals=None):
        """Override to keep track of partners notified by email for
        mail templates using QWeb.
        """
        res = super()._notify_get_recipients_groups(
            message, model_description, msg_vals=msg_vals
        )
        # res example: (see function documentation in
        # odoo/addons/mail/models/mail_thread.py)
        #
        # ['user', <function MailThread._notify_get_recipients_groups.<locals>.<lambda> at 0x7f0978ce1c60>, {'active': True, 'has_button_access': True}],  # noqa: E501
        # ['portal', <function MailThread._notify_get_recipients_groups.<locals>.<lambda> at 0x7f0978ce1d00>, {'active': False, 'has_button_access': False}],  # noqa: E501
        # ['follower', <function MailThread._notify_get_recipients_groups.<locals>.<lambda> at 0x7f0978ce19e0>, {'active': False, 'has_button_access': False}],  # noqa: E501
        # ['customer', <function MailThread._notify_get_recipients_groups.<locals>.<lambda> at 0x7f0978ce1a80>, {'active': True, 'has_button_access': False}]  # noqa: E501
        return res

    # TODO: Write a test for this method
    # was named `_notify_classify_recipients` in Odoo 14.0
    def _notify_get_recipients_classify(
        self, message, recipients_data, model_description, msg_vals=None
    ):
        """The purpose of this hook is to make a copy of `recipients` data because this
        value will be dropped (using pop) before template rendering.
        TODO: Check if this is still true in Odoo 18
        """
        # recipients_data example:
        # [
        #     {
        #         "active": True,
        #         "id": 250,
        #         "is_follower": True,
        #         "lang": "en_US",
        #         "groups": {1, 7},
        #         "notif": "email",
        #         "share": False,
        #         "uid": 197,
        #         "ushare": False,
        #         "type": "user",
        #     }
        # ]
        res = super()._notify_get_recipients_classify(
            message, recipients_data, model_description, msg_vals=msg_vals
        )

        # res example: (see function documentation in
        # odoo/addons/mail/models/mail_thread.py)
        # [
        #     {
        #         "active": True,
        #         "has_button_access": True,
        #         "actions": [],
        #         "notification_group_name": "user",
        #         "recipients": [240],
        #         "button_access": {
        #             "url": "http://localhost:8018/mail/view?model=fake.model.without.name&res_id=1",  # noqa: E501
        #             "title": "View fake.model.without.name",
        #         },
        #     }
        # ]
        for group_data in res:
            recipient_ids = group_data["recipients"]
            group_data["_origin"] = "mail_qweb"
            group_data["_recipients"] = self.env["res.partner"].browse(recipient_ids)
            group_data["_notif_mode"] = {}
            for r in recipients_data:
                if r["id"] in recipient_ids:
                    group_data["_notif_mode"][r["id"]] = r["notif"]
        return res

    # TODO: Write a test for this method
    # was named `_notify_record_by_email` in Odoo 14.0
    def _notify_thread_by_email(
        self,
        message,
        recipients_data,
        msg_vals=False,
        mail_auto_delete=True,  # mail.mail
        model_description=False,
        force_email_company=False,
        force_email_lang=False,  # rendering
        subtitles=None,  # rendering
        resend_existing=False,
        force_send=True,
        send_after_commit=True,  # email send
        **kwargs,
    ):
        """Add a list of textual recipients to the template context in order to
        to write who are notified of this message
        """
        # partners_data = recipients_data["partners"]
        model = msg_vals.get("model") if msg_vals else message.model
        model_name = model_description or (
            self._fallback_lang().env["ir.model"]._get(model).display_name
            if model
            else False
        )  # one query for display name
        recipients_groups_data = self._notify_get_recipients_classify(
            message, recipients_data, model_name, msg_vals=msg_vals
        )
        if not msg_vals:
            msg_vals = {}
        msg_vals["recipients_groups_data"] = recipients_groups_data
        return super()._notify_thread_by_email(
            message,
            recipients_data,
            msg_vals=msg_vals,
            mail_auto_delete=mail_auto_delete,
            model_description=model_description,
            force_email_company=force_email_company,
            force_email_lang=force_email_lang,
            subtitles=subtitles,
            resend_existing=resend_existing,
            force_send=force_send,
            send_after_commit=send_after_commit,
            **kwargs,
        )

    # TODO: Write a test for this method
    # was named `_notify_prepare_template_context` in Odoo 14.0
    def _notify_by_email_prepare_rendering_context(
        self,
        message,
        msg_vals=False,
        model_description=False,
        force_email_company=False,
        force_email_lang=False,
    ):
        """All default template values are set from this function:
        # message
        - is_discussion: boolean
        - message: mail.message
        - subtype: mail.message.subtype
        - tracking_values: list
        # record
        - model_description: char
        - record: module.model
        - record_name: char
        - subtitles
        # user / environment
        - author_user
        - company: res.company
        - email_add_signature
        - lang: char
        - signature: char
        - website_url: char
        # tools
        - is_html_empty
        # display
        - email_notification_force_header
        - email_notification_force_footer
        - email_notification_allow_header
        - email_notification_allow_footer
        """
        res = super()._notify_by_email_prepare_rendering_context(
            message,
            msg_vals=msg_vals,
            model_description=model_description,
            force_email_company=force_email_company,
            force_email_lang=force_email_lang,
        )
        if "object" not in res:
            res["object"] = res["record"]
        res["recipients_groups_data"] = msg_vals["recipients_groups_data"]
        res["content_message_align"] = self._get_notify_content_message_align(message)
        return res

    def _get_notify_content_message_align(self, message):
        """Detect if center alignment should be enabled (based of length of text,
        format complexity, etc.)"""
        align = "left"
        try:
            root = lxml.html.fromstring(message.body)
            for node in root.iter():
                rawtext_length = len(node.text_content())
                subtag_count = 0
                for subnodes in node.getchildren():
                    if subnodes.tag not in (
                        "b",
                        "i",
                        "u",
                        "font",
                        "span",
                        "br",
                        "a",
                        "small",
                    ):
                        subtag_count += 1
                # basic message, without specific formatting
                if subtag_count == 0:
                    # short message
                    if rawtext_length <= 128:
                        align = "center"
                    else:
                        align = "justify"
                # don't go deeper
                break
        except (TypeError, lxml.etree.XMLSyntaxError, lxml.etree.ParserError):
            _logger.debug("Failure parsing this HTML:\n%s", message.body)
        return align

    # TODO: Write a test for this method
    def message_notify(
        self,
        *,
        body="",
        subject=False,
        author_id=None,
        email_from=None,
        model=False,
        res_id=False,
        subtype_xmlid=None,
        subtype_id=False,
        partner_ids=False,
        attachments=None,
        attachment_ids=None,
        **kwargs,
    ):
        """Odoo's shortcut to notify subscribers of messages without publishing on the
        chat."""
        if (
            kwargs
            and kwargs.get("email_layout_xmlid") == "mail.mail_notification_light"
        ):
            # force signature for light template
            kwargs["add_sign"] = True
        return super().message_notify(
            body=body,
            subject=subject,
            author_id=author_id,
            email_from=email_from,
            model=model,
            res_id=res_id,
            subtype_xmlid=subtype_xmlid,
            subtype_id=subtype_id,
            partner_ids=partner_ids,
            attachments=attachments,
            attachment_ids=attachment_ids,
            **kwargs,
        )
