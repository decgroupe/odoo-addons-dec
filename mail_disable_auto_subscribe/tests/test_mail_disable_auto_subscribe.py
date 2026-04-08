# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo import fields

from .common import TestMailDisableAutoSubscribeCommon


class TestMailDisableAutoSubscribe(TestMailDisableAutoSubscribeCommon):
    """Tests for mail_disable_auto_subscribe module."""

    def test_01_res_partner_fields(self):
        """Fields auto_subscribe_on_* exist on res.partner with correct defaults."""
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.assertTrue(partner.auto_subscribe_on_tag)
        self.assertTrue(partner.auto_subscribe_on_message)
        self.assertTrue(partner.auto_subscribe_on_activity)

    def test_02_res_partner_form_view_fields(self):
        """Fields auto_subscribe_on_* are present in the user preferences form view."""
        view_info = self.env["res.users"].get_view(
            view_id=self.env.ref(
                "mail_disable_auto_subscribe.res_users_preferences_form_view"
            ).id,
            view_type="form",
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("auto_subscribe_on_tag", field_names)
        self.assertIn("auto_subscribe_on_message", field_names)
        self.assertIn("auto_subscribe_on_activity", field_names)

    def test_03_res_users_form_view_fields(self):
        """Fields auto_subscribe_on_* are present in the main user form view."""
        view_info = self.env["res.users"].get_view(
            view_id=self.env.ref("mail_disable_auto_subscribe.res_users_form_view").id,
            view_type="form",
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("auto_subscribe_on_tag", field_names)
        self.assertIn("auto_subscribe_on_message", field_names)
        self.assertIn("auto_subscribe_on_activity", field_names)

    def test_04_mail_message_subtype_form_view_fields(self):
        """Field excluded_res_model_ids is present in the subtype form view."""
        view_info = self.env["mail.message.subtype"].get_view(
            view_id=self.env.ref(
                "mail_disable_auto_subscribe.mail_message_subtype_form_view"
            ).id,
            view_type="form",
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("excluded_res_model_ids", field_names)

    def test_05_res_users_self_writeable_fields(self):
        """auto_subscribe fields are in SELF_WRITEABLE_FIELDS for res.users."""
        self.assertIn("auto_subscribe_on_tag", self.env.user.SELF_WRITEABLE_FIELDS)
        self.assertIn("auto_subscribe_on_message", self.env.user.SELF_WRITEABLE_FIELDS)
        self.assertIn("auto_subscribe_on_activity", self.env.user.SELF_WRITEABLE_FIELDS)

    def test_06_message_subscribe_manual_context(self):
        """Direct message_subscribe call sets manual_message_subscribe context."""
        # create a thread-enabled record to subscribe to
        partner_subject = self.env["res.partner"].create({"name": "Subject"})
        # subscribe a partner manually (without autofollow context)
        partner_subject.message_subscribe(partner_ids=[self.partner_all.id])
        # verify the partner is now a follower
        follower = self.env["mail.followers"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", partner_subject.id),
                ("partner_id", "=", self.partner_all.id),
            ]
        )
        self.assertTrue(follower)

    def test_07_auto_subscribe_on_message_disabled_prevents_author_follow(
        self,
    ):
        """Author with auto_subscribe_on_message=False is not auto-subscribed
        on post."""
        # partner_none has auto_subscribe_on_message=False — use it as explicit author
        # create without subscribe so the only subscription path is via message_post
        partner_subject = (
            self.env["res.partner"]
            .with_context(mail_create_nosubscribe=True)
            .create({"name": "Message Subject"})
        )
        partner_subject.message_post(
            body="hello",
            message_type="comment",
            author_id=self.partner_none.id,
        )
        # the author should NOT have been added as a follower because they opted out
        follower = self.env["mail.followers"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", partner_subject.id),
                ("partner_id", "=", self.partner_none.id),
            ]
        )
        self.assertFalse(follower)

    def test_08_auto_subscribe_on_message_enabled_adds_author_as_follower(
        self,
    ):
        """Author with auto_subscribe_on_message=True is auto-subscribed on post."""
        # partner_all has auto_subscribe_on_message=True — use it as explicit author
        # do NOT use mail_create_nosubscribe=True here: that context would leak onto
        # the returned record and suppress author subscription in message_post
        partner_subject = self.env["res.partner"].create({"name": "Message Subject 2"})
        partner_subject.message_post(
            body="hello sub",
            message_type="comment",
            author_id=self.partner_all.id,
        )
        # the author SHOULD have been added as a follower
        follower = self.env["mail.followers"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", partner_subject.id),
                ("partner_id", "=", self.partner_all.id),
            ]
        )
        self.assertTrue(follower)

    def test_09_excluded_model_filters_default_subtypes(self):
        """Subtypes with a model in excluded_res_model_ids are not default
        for that model."""
        # fetch a default subtype and add res.partner as excluded
        discussion_subtype = self.env.ref("mail.mt_comment")
        partner_model = self.env["ir.model"].search(
            [("model", "=", "res.partner")], limit=1
        )
        discussion_subtype.excluded_res_model_ids = [(4, partner_model.id)]
        # clear the cache so the filter is applied
        self.MailSubtype.invalidate_model()
        # the subtype should not appear in defaults for res.partner
        subtype_ids, internal_ids, external_ids = self.MailSubtype._default_subtypes(
            "res.partner"
        )
        self.assertNotIn(discussion_subtype.id, subtype_ids)
        # clean up
        discussion_subtype.excluded_res_model_ids = [(3, partner_model.id)]

    def test_10_filter_subtypes_skipped_when_manual_subscribe(self):
        """Filtering is skipped when manual_message_subscribe is in context."""
        discussion_subtype = self.env.ref("mail.mt_comment")
        partner_model = self.env["ir.model"].search(
            [("model", "=", "res.partner")], limit=1
        )
        discussion_subtype.excluded_res_model_ids = [(4, partner_model.id)]
        self.MailSubtype.invalidate_model()
        # with manual_message_subscribe, the exclusion should not apply
        subtype_ids, _int, _ext = self.MailSubtype.with_context(
            manual_message_subscribe=True
        )._default_subtypes("res.partner")
        self.assertIn(discussion_subtype.id, subtype_ids)
        # clean up
        discussion_subtype.excluded_res_model_ids = [(3, partner_model.id)]

    def test_11_auto_subscribe_on_tag_filtered(self):
        """Partners with auto_subscribe_on_tag=False are not subscribed
        via autofollow."""
        partner_subject = self.env["res.partner"].create({"name": "Tag Subject"})
        # simulate autofollow context (tag mention)
        partner_subject.with_context(mail_post_autofollow=True).message_subscribe(
            partner_ids=[self.partner_none.id]
        )
        follower = self.env["mail.followers"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", partner_subject.id),
                ("partner_id", "=", self.partner_none.id),
            ]
        )
        self.assertFalse(follower)

    def test_12_auto_subscribe_on_tag_allowed(self):
        """Partners with auto_subscribe_on_tag=True are subscribed via autofollow."""
        partner_subject = self.env["res.partner"].create({"name": "Tag Subject 2"})
        partner_subject.with_context(mail_post_autofollow=True).message_subscribe(
            partner_ids=[self.partner_all.id]
        )
        follower = self.env["mail.followers"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", partner_subject.id),
                ("partner_id", "=", self.partner_all.id),
            ]
        )
        self.assertTrue(follower)

    def test_13_activity_create_subscribes_user_when_activity_enabled(self):
        """User with auto_subscribe_on_activity=True is subscribed
        on activity create."""
        partner_subject = (
            self.env["res.partner"]
            .with_context(mail_create_nosubscribe=True)
            .create({"name": "Activity Subject"})
        )
        activity_type = self.env.ref("mail.mail_activity_data_todo")
        self.env["mail.activity"].create(
            {
                "res_model_id": self.env["ir.model"]._get("res.partner").id,
                "res_id": partner_subject.id,
                "activity_type_id": activity_type.id,
                "user_id": self.user_all.id,
                "date_deadline": fields.Date.today(),
            }
        )
        follower = self.env["mail.followers"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", partner_subject.id),
                ("partner_id", "=", self.user_all.partner_id.id),
            ]
        )
        self.assertTrue(follower)

    def test_14_activity_create_does_not_subscribe_user_when_activity_disabled(
        self,
    ):
        """User with auto_subscribe_on_activity=False is not subscribed
        on activity create."""
        partner_subject = (
            self.env["res.partner"]
            .with_context(mail_create_nosubscribe=True)
            .create({"name": "Activity Subject 2"})
        )
        activity_type = self.env.ref("mail.mail_activity_data_todo")
        self.env["mail.activity"].create(
            {
                "res_model_id": self.env["ir.model"]._get("res.partner").id,
                "res_id": partner_subject.id,
                "activity_type_id": activity_type.id,
                "user_id": self.user_none.id,
                "date_deadline": fields.Date.today(),
            }
        )
        follower = self.env["mail.followers"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", partner_subject.id),
                ("partner_id", "=", self.user_none.partner_id.id),
            ]
        )
        self.assertFalse(follower)

    def test_15_activity_write_subscribes_new_user_when_activity_enabled(self):
        """Reassigning activity to user with auto_subscribe_on_activity=True
        subscribes them."""
        partner_subject = (
            self.env["res.partner"]
            .with_context(mail_create_nosubscribe=True)
            .create({"name": "Activity Subject 3"})
        )
        activity_type = self.env.ref("mail.mail_activity_data_todo")
        activity = self.env["mail.activity"].create(
            {
                "res_model_id": self.env["ir.model"]._get("res.partner").id,
                "res_id": partner_subject.id,
                "activity_type_id": activity_type.id,
                "user_id": self.user_none.id,
                "date_deadline": fields.Date.today(),
            }
        )
        # reassign to user_all (allows activity-based subscription)
        activity.write({"user_id": self.user_all.id})
        follower = self.env["mail.followers"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", partner_subject.id),
                ("partner_id", "=", self.user_all.partner_id.id),
            ]
        )
        self.assertTrue(follower)

    def test_16_activity_write_does_not_subscribe_new_user_when_activity_disabled(
        self,
    ):
        """Reassigning activity to user with auto_subscribe_on_activity=False
        does not subscribe them."""
        partner_subject = (
            self.env["res.partner"]
            .with_context(mail_create_nosubscribe=True)
            .create({"name": "Activity Subject 4"})
        )
        activity_type = self.env.ref("mail.mail_activity_data_todo")
        activity = self.env["mail.activity"].create(
            {
                "res_model_id": self.env["ir.model"]._get("res.partner").id,
                "res_id": partner_subject.id,
                "activity_type_id": activity_type.id,
                "user_id": self.user_all.id,
                "date_deadline": fields.Date.today(),
            }
        )
        # reassign to user_none (refuses activity-based subscription)
        activity.write({"user_id": self.user_none.id})
        follower = self.env["mail.followers"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", partner_subject.id),
                ("partner_id", "=", self.user_none.partner_id.id),
            ]
        )
        self.assertFalse(follower)
