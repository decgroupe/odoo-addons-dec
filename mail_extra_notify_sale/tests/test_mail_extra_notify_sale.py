# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024


from odoo.addons.mail_extra_notify.tests.common import TestMailExtraNotifyCommon, tagged
from odoo.addons.mail.tests.common import mail_new_test_user


@tagged("post_install", "-at_install")
class TestMailExtraNotifySale(TestMailExtraNotifyCommon):

    def setUp(self):
        super().setUp()
        sale_order_id_xml_id = "sale.sale_order_7"
        self.sale_order_id = self.env.ref(sale_order_id_xml_id)
        # set an opportunity
        self.sale_order_id.opportunity_id = self.env.ref("crm.crm_case_20")

    def test_01_assigned_sheet_more_informations(self):
        try:
            self.mail_unlink_disabled()
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # set salesperson
            self.sale_order_id.user_id = self.user1
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "You have been assigned to S00007",
            )
            self.assertIn("Opportunity", mail_id.body)
            self.assertIn("Delivery Address", mail_id.body)
            self.assertIn("Total", mail_id.body)
        finally:
            self.mail_unlink_enabled()

    def test_02_assigned_activity_more_informations(self):
        try:
            self.mail_unlink_disabled()
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # assign an activity
            activity_id = self.sale_order_id.activity_schedule(
                act_type_xmlid="mail.mail_activity_data_todo",
                note="Please check this",
                user_id=self.user1.id,
            )
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "S00007: To Do assigned to you",
            )
            self.assertIn("Opportunity", mail_id.body)
            self.assertIn("Delivery Address", mail_id.body)
            self.assertIn("Total", mail_id.body)
        finally:
            self.mail_unlink_enabled()
