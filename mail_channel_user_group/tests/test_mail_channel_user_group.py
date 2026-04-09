# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from .common import MailChannelUserGroupCommon


class TestMailChannelUserGroup(MailChannelUserGroupCommon):
    """Tests for mail_channel_user_group module."""

    def test_01_user_group_restored_for_internal_users(self):
        """Check that internal users get user group, not customer group.
        In base Odoo 18.0, discuss.channel forces all non-customer groups
        to a no-match lambda. This module restores the user group for
        internal channel recipients.
        """
        msg = self.channel.message_post(
            body="Test message for internal user",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            partner_ids=[self.partner_internal.id],
        )
        # simulate an internal user recipient data as produced by _notify_get_recipients
        user_recipient_data = {
            "active": True,
            "id": self.partner_internal.id,
            "is_follower": False,
            "groups": [],
            "lang": self.partner_internal.lang,
            "notif": "email",
            "share": False,
            "type": "user",
            "uid": self.user_internal.id,
            "ushare": False,
        }
        # _notify_get_recipients_groups returns a list of [name, func, data]
        raw_groups = self.channel._notify_get_recipients_groups(msg, "Discuss Channel")
        user_group_entry = next((g for g in raw_groups if g[0] == "user"), None)
        self.assertIsNotNone(user_group_entry, "user group must exist")
        group_name, group_func, group_data = user_group_entry
        # the user group func must accept an internal user recipient
        self.assertTrue(
            group_func(user_recipient_data),
            "user group func must match internal user recipient (type=='user')",
        )
        # the has_button_access must be hidden for channel messages
        self.assertFalse(
            group_data.get("has_button_access", True),
            "has_button_access must be False for channel user group",
        )

    def test_02_customer_recipient_not_classified_as_user(self):
        """Check that a customer (external partner) does not match the user group.
        The user group lambda checks pdata['type'] == 'user', so a recipient
        with type=='customer' must not match the user group.
        """
        msg = self.channel.message_post(
            body="Test message",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        customer_recipient_data = {
            "active": True,
            "id": self.partner_internal.id,
            "is_follower": False,
            "groups": [],
            "lang": "en_US",
            "notif": "email",
            "share": True,
            "type": "customer",
            "uid": False,
            "ushare": True,
        }
        raw_groups = self.channel._notify_get_recipients_groups(msg, "Discuss Channel")
        user_group_entry = next((g for g in raw_groups if g[0] == "user"), None)
        self.assertIsNotNone(user_group_entry, "user group must exist")
        group_func = user_group_entry[1]
        # customer type must NOT match the user group
        self.assertFalse(
            group_func(customer_recipient_data),
            "user group func must not match a customer recipient (type=='customer')",
        )
