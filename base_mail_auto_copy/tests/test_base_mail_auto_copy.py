# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024


from odoo.tests import tagged

from .common import MSG_CONTACT, TestBaseMailAutoCopyCommon


class TestBaseMailAutoCopy(TestBaseMailAutoCopyCommon):
    def setUp(self):
        super().setUp()

    def test_01_get_server(self):
        # get server with no args
        mail_server = self.env["ir.mail_server"].get_mail_server(
            mail_server_id=False, smtp_server=False
        )
        self.assertEqual(mail_server, self.primary_mail_server)
        # get server with server ID
        mail_server = self.env["ir.mail_server"].get_mail_server(
            mail_server_id=self.primary_mail_server.id, smtp_server=False
        )
        self.assertEqual(mail_server, self.primary_mail_server)
        # get server with another server ID
        mail_server = self.env["ir.mail_server"].get_mail_server(
            mail_server_id=self.secondary_mail_server.id, smtp_server=False
        )
        self.assertEqual(mail_server, self.secondary_mail_server)
        # get server with server ID and smtp host
        mail_server = self.env["ir.mail_server"].get_mail_server(
            mail_server_id=self.primary_mail_server.id, smtp_server="smtp.mydomain.com"
        )
        self.assertEqual(mail_server, self.primary_mail_server)
        # get server with smtp host
        mail_server = self.env["ir.mail_server"].get_mail_server(
            mail_server_id=False, smtp_server="smtp.mydomain.com"
        )
        self.assertEqual(mail_server, False)

    def test_02_unknown_user(self):
        def check(message):
            self.assertNotIn("Bcc", message)
            self.assertNotIn("Cc", message)

        mail_server = self._get_mail_server()
        self.assertTrue(mail_server.auto_add_sender)
        res = self._send_email(self._get_message_from_john_to_jane(), check)
        self.assertEqual(res, self.MESSAGE_ID)

    def test_03_user_copy_yes(self):
        mail_server = self._get_mail_server()
        self.assertTrue(mail_server.auto_add_sender)
        user = self._create_user("john@example.com")
        user.copy_sent_email = True

        def check(message):
            self.assertIn("Bcc", message)
            self.assertEqual(message["Bcc"], "John Doe <john@example.com>")
            self.assertNotIn("Cc", message)

        res = self._send_email(self._get_message_from_john_to_jane(), check)
        self.assertEqual(res, self.MESSAGE_ID)

        # same test without active server
        self._disable_all_servers()
        mail_server = self._get_mail_server()
        self.assertFalse(mail_server)

        def check(message):
            self.assertNotIn("Bcc", message)
            self.assertNotIn("Cc", message)

        res = self._send_email(self._get_message_from_john_to_jane(), check)
        self.assertEqual(res, self.MESSAGE_ID)

    def test_04_user_copy_no(self):
        mail_server = self._get_mail_server()
        self.assertTrue(mail_server.auto_add_sender)
        user = self._create_user("john@example.com")
        user.copy_sent_email = False

        def check(message):
            self.assertNotIn("Bcc", message)
            self.assertNotIn("Cc", message)

        res = self._send_email(self._get_message_from_john_to_jane(), check)
        self.assertEqual(res, self.MESSAGE_ID)

    def test_05_user_copy_yes_but_server_no(self):
        mail_server = self._get_mail_server(False)
        self.assertFalse(mail_server.auto_add_sender)
        user = self._create_user("john@example.com")
        user.copy_sent_email = True

        def check(message):
            self.assertNotIn("Bcc", message)
            self.assertNotIn("Cc", message)

        res = self._send_email(self._get_message_from_john_to_jane(), check)
        self.assertEqual(res, self.MESSAGE_ID)

    def test_06_global_cc(self):
        mail_server = self._get_mail_server()
        mail_server.auto_cc_addresses = "aladdin@test.example.com"

        def check(message):
            self.assertNotIn("Bcc", message)
            self.assertIn("Cc", message)
            self.assertEqual(message["Cc"], "aladdin@test.example.com")

        res = self._send_email(self._get_message_from_john_to_jane(), check)
        self.assertEqual(res, self.MESSAGE_ID)

    def test_07_global_cc_with_existing_cc(self):
        mail_server = self._get_mail_server()
        mail_server.auto_cc_addresses = "aladdin@test.example.com"
        # user = self._create_user("john@example.com")
        # user.copy_sent_email = False

        def check(message):
            self.assertNotIn("Bcc", message)
            self.assertIn("Cc", message)
            self.assertEqual(
                message["Cc"], "jasmine@test.example.com, aladdin@test.example.com"
            )

        msg = self._get_message_from_john_to_jane()
        msg["Cc"] = "jasmine@test.example.com"

        res = self._send_email(msg, check)
        self.assertEqual(res, self.MESSAGE_ID)

    def test_08_global_bcc(self):
        mail_server = self._get_mail_server()
        mail_server.auto_bcc_addresses = "archive_copy@example.com"

        def check(message):
            self.assertIn("Bcc", message)
            self.assertEqual(message["Bcc"], "archive_copy@example.com")
            self.assertNotIn("Cc", message)

        msg = self._get_message_from_john_to_jane()
        res = self._send_email(msg, check)
        self.assertEqual(res, self.MESSAGE_ID)

    def test_09_global_bcc_existing_header(self):
        mail_server = self._get_mail_server()
        mail_server.auto_bcc_addresses = "archive_copy@example.com"

        def check(message):
            self.assertIn("Bcc", message)
            self.assertEqual(
                message["Bcc"], "archive_copy#2@example.com, archive_copy@example.com"
            )
            self.assertNotIn("Cc", message)

        msg = self._get_message_from_john_to_jane()
        msg["Bcc"] = "archive_copy#2@example.com"
        res = self._send_email(msg, check)
        self.assertEqual(res, self.MESSAGE_ID)

    def test_09_global_bcc_existing_header_existing_user(self):
        mail_server = self._get_mail_server()
        mail_server.auto_bcc_addresses = "archive_copy@example.com"
        user = self._create_user("john@example.com")
        user.copy_sent_email = True

        def check(message):
            self.assertIn("Bcc", message)
            self.assertEqual(
                message["Bcc"],
                "archive_copy#2@example.com, "
                "archive_copy@example.com, "
                "John Doe <john@example.com>",
            )
            self.assertNotIn("Cc", message)

        msg = self._get_message_from_john_to_jane()
        msg["Bcc"] = "archive_copy#2@example.com"
        res = self._send_email(msg, check)
        self.assertEqual(res, self.MESSAGE_ID)

    def test_10_always_ignore(self):
        mail_server = self._get_mail_server()
        self.assertTrue(mail_server.auto_add_sender)
        mail_server.ignored_aas_addresses = "john@example.com"
        user = self._create_user("john@example.com")
        user.copy_sent_email = True

        def check(message):
            self.assertNotIn("Bcc", message)
            self.assertNotIn("Cc", message)

        res = self._send_email(self._get_message_from_john_to_jane(), check)
        self.assertEqual(res, self.MESSAGE_ID)

    def test_11_incoming(self):
        incoming_message = MSG_CONTACT
        with self.assertRaisesRegex(
            ValueError, "No possible route found for incoming message"
        ):
            self.env["mail.thread"].message_process(None, incoming_message)


@tagged("post_install", "-at_install")
class TestBaseMailAutoCopyPost(TestBaseMailAutoCopyCommon):
    """Use post install to ensure other modules overriding base templates will be
    fully loaded to override qcontext properly
    """

    def test_01_disable_cc_when_channel(self):
        """BCC auto-copy must be disabled when email originates from a mail group."""
        user_john = self._create_user("john@example.com")
        user_john.copy_sent_email = True
        user_jane = self._create_user("jane@example.com")
        # create a mail group and add john and jane as members
        mail_group = self.env["mail.group"].create(
            {
                "name": "General (YES)",
                "description": "General Mailing-List for MyTestCompany",
                "access_mode": "public",
            }
        )
        self.env["mail.group.member"].create(
            [
                {
                    "mail_group_id": mail_group.id,
                    "partner_id": user_john.partner_id.id,
                },
                {
                    "mail_group_id": mail_group.id,
                    "partner_id": user_jane.partner_id.id,
                },
            ]
        )
        # get mail server and verify auto_add_sender is enabled
        mail_server = self._get_mail_server()
        self.assertTrue(mail_server.auto_add_sender)
        # post message from john: group notifies jane (john is skipped as author)
        message_id = mail_group.message_post(
            author_id=user_john.partner_id.id,
            email_from=user_john.partner_id.email_formatted,
            body="Test",
            subject="Test Subject",
        )
        # exactly one outgoing mail should be created for jane
        mail_id = message_id.mail_ids
        self.assertEqual(len(mail_id), 1)
        self.assertEqual(mail_id.email_to, user_jane.email)

        # build raw email; even with copy_sent_email=True for john, auto-BCC must
        # be suppressed because the message originates from a mail group
        def check(message):
            self.assertNotIn("Bcc", message)
            self.assertNotIn("Cc", message)

        msg = self._build_email_from_mail(mail_id, to=user_jane.email)
        res = self._send_email(msg, check)
        self.assertEqual(res, mail_id.message_id)

    def test_02_send_mail_from_template(self):
        # brandon.freeman55@example.com
        partner_id = self.env.ref("base.res_partner_address_15")
        # retrieve demo template
        template_id = self.env.ref("base_mail_auto_copy.test_template")
        self.assertEqual(template_id.reply_to, False)
        # send mail #1
        mail_res_id = template_id.send_mail(res_id=partner_id.id, force_send=True)
        self.assertGreaterEqual(mail_res_id, 1)
        mail_id = self.env["mail.mail"].browse(mail_res_id)
        self.assertEqual(mail_id.email_from, "brandon.freeman55@example.com")
        self.assertEqual(mail_id.reply_to, "brandon.freeman55@example.com")
        self.assertEqual(mail_id.email_to, "fake@domain.com")
        # unset 'from': Note that there is protection against void 'email_from' in
        # `send_mail`, the value is popped out if False or empty. A default value is
        # then set from '/odoo/addons/mail/models/mail_message.py:Message.default_get'
        template_id.email_from = False
        # send mail #2
        mail_res_id = template_id.send_mail(res_id=partner_id.id, force_send=True)
        self.assertGreaterEqual(mail_res_id, 1)
        mail_id = self.env["mail.mail"].browse(mail_res_id)
        self.assertEqual(mail_id.email_from, '"OdooBot" <odoobot@example.com>')
        self.assertEqual(mail_id.reply_to, '"OdooBot" <odoobot@example.com>')
        self.assertEqual(mail_id.email_to, "fake@domain.com")
        # custom 'from'
        template_id.email_from = "contact@example.com"
        # send mail #3
        mail_res_id = template_id.send_mail(res_id=partner_id.id, force_send=True)
        self.assertGreaterEqual(mail_res_id, 1)
        mail_id = self.env["mail.mail"].browse(mail_res_id)
        self.assertEqual(mail_id.email_from, "contact@example.com")
        self.assertEqual(mail_id.reply_to, "contact@example.com")
        self.assertEqual(mail_id.email_to, "fake@domain.com")

    def test_03_send_mail_message_empty_from(self):
        demo_message = self.env.ref("mail.mail_message_channel_1_2_1")
        message_id = self.env["mail.message"].create(
            {
                "message_type": "email",
                "email_from": False,
                "model": demo_message.model,
                "res_id": demo_message.res_id,
            }
        )
        self.assertEqual(message_id.email_from, '"OdooBot" <odoobot@example.com>')
        message_id = self.env["mail.message"].create(
            {
                "message_type": "email",
                "email_from": "",
                "model": demo_message.model,
                "res_id": demo_message.res_id,
            }
        )
        self.assertEqual(message_id.email_from, '"OdooBot" <odoobot@example.com>')
