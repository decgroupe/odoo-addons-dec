# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

from functools import partial

from odoo.addons.mail.tests.common import MailCommon
from odoo.tests import new_test_user

mail_new_test_user = partial(
    new_test_user,
    context={
        "mail_create_nolog": True,
        "mail_create_nosubscribe": True,
        "mail_notrack": True,
        "no_reset_password": True,
    },
)


class TestMailChannelNotifyEmail(MailCommon):
    """ """

    def _join_channel(self, channel, partners):
        for partner in partners:
            channel.write(
                {"channel_last_seen_partner_ids": [(0, 0, {"partner_id": partner.id})]}
            )
        channel.invalidate_cache()

    def _leave_channel(self, channel, partners):
        for partner in partners:
            channel._action_unfollow(partner)

    @classmethod
    def setUpClass(cls):
        super(TestMailChannelNotifyEmail, cls).setUpClass()
        cls.user_jasmine = mail_new_test_user(
            cls.env,
            login="jasmine",
            groups="base.group_user",
            company_id=cls.company_admin.id,
            name="Jasmine",
            email="jasmine@test.example.com",
            notification_type="inbox",
            signature="--\nJasmine",
        )
        cls.user_aladdin = mail_new_test_user(
            cls.env,
            login="aladdin",
            groups="base.group_user",
            company_id=cls.company_admin.id,
            name="Aladdin",
            email="aladdin@test.example.com",
            notification_type="email",
            signature="--\nAladdin",
        )

        cls.general_channel_with_email = cls.env["mail.channel"].create(
            {
                "name": "General (YES)",
                "description": "General Mailing-List for MyTestCompany",
                "alias_name": "general_email",
                "public": "groups",
                "email_send": True,
            }
        )
        cls.general_channel_no_email = cls.env["mail.channel"].create(
            {
                "name": "General (NO)",
                "description": "General Odoo's Channel for MyTestCompany",
                "alias_name": "general_odoo",
                "public": "groups",
                "email_send": False,
            }
        )

    def test_01_channel_yes_send_msg_on_post(self):
        self._join_channel(
            self.general_channel_with_email, self.user_jasmine.partner_id
        )
        self._join_channel(
            self.general_channel_with_email, self.user_aladdin.partner_id
        )

        message_id = self.general_channel_with_email.message_post(
            body="Test",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            mail_auto_delete=False,
        )
        mail_id = message_id.mail_ids
        self.assertEqual(len(mail_id), 1)
        self.assertIn("aladdin@test.example.com", mail_id.email_to)
        self.assertIn("jasmine@test.example.com", mail_id.email_to)

    def test_02_channel_no_send_msg_on_post(self):
        self._join_channel(self.general_channel_no_email, self.user_jasmine.partner_id)
        self._join_channel(self.general_channel_no_email, self.user_aladdin.partner_id)

        message_id = self.general_channel_no_email.message_post(
            body="Test",
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            mail_auto_delete=False,
        )
        mail_id = message_id.mail_ids
        self.assertFalse(mail_id)
