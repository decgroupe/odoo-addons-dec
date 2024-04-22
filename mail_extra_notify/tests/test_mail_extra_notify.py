# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo.tests import tagged
from odoo.addons.mail_extra_notify.tests.common import TestMailExtraNotifyCommon


@tagged("post_install", "-at_install")
class TestMailExtraNotify(TestMailExtraNotifyCommon):

    def setUp(self):
        super().setUp()
        partner_xml_id = "base.res_partner_address_15"
        self.partner_id = self.env.ref(partner_xml_id)

    def test_01_assigned_partner_more_informations(self):
        try:
            self.mail_unlink_disabled()
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # set salesperson
            self.partner_id.user_id = self.user1
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "You have been assigned to Azure Interior, Brandon Freeman",
            )
            self.assertIn("Email", mail_id.body)
            self.assertIn("Created on", mail_id.body)
            self.assertIn("Created by", mail_id.body)
        finally:
            self.mail_unlink_enabled()

    def test_02_assigned_activity_more_informations(self):
        try:
            self.mail_unlink_disabled()
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # assign an activity
            activity_id = self.partner_id.activity_schedule(
                act_type_xmlid="mail.mail_activity_data_todo",
                note="Please check this",
                user_id=self.user1.id,
            )
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "Azure Interior, Brandon Freeman: To Do assigned to you",
            )
            self.assertIn("Email", mail_id.body)
            self.assertIn("Created on", mail_id.body)
            self.assertIn("Created by", mail_id.body)
        finally:
            self.mail_unlink_enabled()
