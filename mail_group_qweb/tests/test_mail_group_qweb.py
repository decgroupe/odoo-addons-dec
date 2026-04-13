# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from .common import TestMailGroupQwebCommon


class TestMailGroupQweb(TestMailGroupQwebCommon):
    """Tests for mail_group_qweb module."""

    def test_01_get_recipient_data_classifies_members(self):
        """Check that _get_recipient_data classifies members by their type."""
        result = self.env["mail.group.member"]._get_recipient_data(self.test_group)
        group_data = result[self.test_group.id]
        # 3 members: customer, internal user, portal user
        self.assertEqual(len(group_data), 3)
        # email-only member must be classified as customer
        customer_data = group_data[self.member_customer.id]
        self.assertEqual(customer_data["type"], "customer")
        # member linked to an internal user must be classified as user
        internal_data = group_data[self.member_internal.id]
        self.assertEqual(internal_data["type"], "user")
        # member linked to a portal user must be classified as portal
        portal_data = group_data[self.member_portal.id]
        self.assertEqual(portal_data["type"], "portal")

    def test_02_get_recipient_data_fields(self):
        """Check that _get_recipient_data returns the expected fields for each
        member."""
        result = self.env["mail.group.member"]._get_recipient_data(self.test_group)
        group_data = result[self.test_group.id]
        for _member_id, data in group_data.items():
            self.assertIn("id", data)
            self.assertIn("email", data)
            self.assertIn("notif", data)
            self.assertIn("share", data)
            self.assertIn("active", data)
            self.assertIn("type", data)

    def test_03_notify_get_recipients_returns_all_members(self):
        """Check that _notify_get_recipients returns one entry per group member."""
        recipients = self.test_group._notify_get_recipients()
        self.assertEqual(len(recipients), len(self.test_group.member_ids))
        # each recipient dict must have the minimum required keys
        for recipient in recipients:
            self.assertIn("id", recipient)
            self.assertIn("email", recipient)
            self.assertIn("notif", recipient)

    def test_04_notify_get_recipients_classify_sets_origin(self):
        """Check that _notify_get_recipients_classify marks each group with _origin."""
        recipients_data = self.test_group._notify_get_recipients()
        groups_data = self.test_group._notify_get_recipients_classify(
            self.test_message,
            recipients_data,
        )
        self.assertTrue(len(groups_data) > 0)
        for group_data in groups_data:
            # each group must be tagged as coming from this module
            self.assertEqual(group_data["_origin"], "mail_group_qweb")
            # _members must be a mail.group.member recordset
            self.assertEqual(group_data["_members"]._name, "mail.group.member")
            # _members_notif_mode must map member ids to notification modes
            self.assertIsInstance(group_data["_members_notif_mode"], dict)
            for member_id in group_data["recipients"]:
                self.assertIn(member_id, group_data["_members_notif_mode"])

    def test_05_notify_by_email_prepare_rendering_context(self):
        """Check that the qweb rendering context has the required keys."""
        recipients_data = self.test_group._notify_get_recipients()
        groups_data = self.test_group._notify_get_recipients_classify(
            self.test_message,
            recipients_data,
        )
        render_ctx = self.test_group._notify_by_email_prepare_rendering_context(
            self.test_message,
            groups_data,
            self.member_customer,
        )
        self.assertIn("message", render_ctx)
        self.assertIn("recipients_groups_data", render_ctx)
        self.assertIn("notification_group_name", render_ctx)
        self.assertIn("content_message_align", render_ctx)
        # message must match the one provided
        self.assertEqual(render_ctx["message"], self.test_message)
        # recipients_groups_data must be the same list
        self.assertEqual(render_ctx["recipients_groups_data"], groups_data)

    def test_06_notify_members_sends_one_email_per_member(self):
        """Check that _notify_members creates one mail.mail per member except the
        author."""
        # track mail records before calling _notify_members
        before_mails = self.Mail.sudo().search([])
        with self.patch_mail_unlink():
            self.test_group._notify_members(self.test_message)
            new_mails = self.Mail.sudo().search([]) - before_mails
            # the outsider sent the message so 3 members must receive it
            self.assertEqual(len(new_mails), 3)
            # the author's email must not be in the recipients
            sent_to = new_mails.mapped("email_to")
            self.assertNotIn("outsider@example.com", sent_to)

    def test_07_notify_members_skips_author(self):
        """Check that _notify_members does not send an email back to the message
        author."""
        # create a message whose author is one of the group members
        message_from_member = self.env["mail.group.message"].create(
            {
                "subject": "Posted by member",
                "mail_group_id": self.test_group.id,
                "email_from": self.member_customer.email,
                "body": "<p>Message from a member.</p>",
            }
        )
        before_mails = self.Mail.sudo().search([])
        with self.patch_mail_unlink():
            self.test_group._notify_members(message_from_member)
            new_mails = self.Mail.sudo().search([]) - before_mails
            # only 2 members should receive the email (member_customer is the author)
            self.assertEqual(len(new_mails), 2)
            sent_to = new_mails.mapped("email_to")
            # the author must not receive their own post
            self.assertNotIn(self.member_customer.email, sent_to)

    def test_08_get_footer_vals_contains_group_name(self):
        """Check that _get_footer_vals includes the group name and unsubscribe URL."""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        unsub_url = f"{base_url}/groups/unsubscribe?token=test"
        vals = self.test_group._get_footer_vals(base_url, unsub_url)
        self.assertIn("group", vals)
        self.assertEqual(vals["group"], self.test_group.name)
        self.assertIn("unsub_url", vals)
        self.assertEqual(vals["unsub_url"], unsub_url)
        self.assertIn("group_url", vals)
        self.assertTrue(vals["group_url"].startswith(base_url))

    def test_09_get_footer_renders_group_info(self):
        """Check that _get_footer renders HTML containing the group name."""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        unsub_url = f"{base_url}/groups/unsubscribe?token=test"
        vals = self.test_group._get_footer_vals(base_url, unsub_url)
        footer = self.test_group._get_footer(vals)
        footer_str = str(footer)
        # footer must reference the group name
        self.assertIn(self.test_group.name, footer_str)
        # footer must include the unsubscribe label
        self.assertIn("Unsubscribe", footer_str)
