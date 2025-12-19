# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo.tests import common, tagged
from odoo.tools import mute_logger

from odoo.addons.mail.tests.common import MailCase
from odoo.addons.mail_remove_gmail_signature.tests.common import MSG_FROM_YFI


@tagged("mail_thread", "mail_gateway")
class TestMailRemoveGmailSignature(common.TransactionCase, MailCase):
    def setUp(self):
        super().setUp()
        group_data = {
            "name": "project-rd-channel",
            "access_mode": "public",
            "alias_name": "project-rd",
            #          or "project-rd@mycompany.com" if not "alias_incoming_local"
            "alias_incoming_local": True,
        }

        self.mail_group_id = self.env["mail.group"].create(group_data)

    @mute_logger("odoo.addons.mail.models.mail_thread")
    def test_01_message_from_our_domain(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "mail.catchall.domain", "mycompany.com"
        )
        incoming_message = MSG_FROM_YFI
        prev_msg_ids = self.mail_group_id.mail_group_message_ids
        record_id = self.env["mail.thread"].message_process(None, incoming_message)
        msg_id = self.mail_group_id.mail_group_message_ids - prev_msg_ids
        self.assertEqual(1, len(msg_id))
        self.assertEqual(self.mail_group_id.id, record_id)
        self.assertNotIn("res_users_signature_workflow_myc", msg_id.body)

    @mute_logger("odoo.addons.mail.models.mail_thread")
    def test_02_message_from_other_domain(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "mail.catchall.domain", "widget.com"
        )
        incoming_message = MSG_FROM_YFI
        prev_msg_ids = self.mail_group_id.mail_group_message_ids
        record_id = self.env["mail.thread"].message_process(None, incoming_message)
        msg_id = self.mail_group_id.mail_group_message_ids - prev_msg_ids
        self.assertEqual(1, len(msg_id))
        self.assertEqual(self.mail_group_id.id, record_id)
        self.assertIn("res_users_signature_workflow_myc", msg_id.body)
