# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024


from odoo.addons.mail_extra_notify.tests.common import TestMailExtraNotifyCommon, tagged
from odoo.addons.mail.tests.common import mail_new_test_user


@tagged("post_install", "-at_install")
class TestMailExtraNotifyHr(TestMailExtraNotifyCommon):

    def setUp(self):
        super().setUp()
        sheet_id_xml_id = "hr_expense.travel_ny_sheet"
        # duplicate existing approved sheet to a new draft one
        self.sheet_id = self.env.ref(sheet_id_xml_id).copy()
        self.expense_user_manager = mail_new_test_user(
            self.env,
            name="Expense manager",
            login="expense_manager_1",
            email="expense_manager_1@example.com",
            notification_type="email",
            groups="base.group_user,hr_expense.group_hr_expense_manager",
            company_ids=[(6, 0, self.env.companies.ids)],
        )

    def test_01_assigned_sheet_more_informations(self):
        try:
            self.mail_unlink_disabled()
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # set salesperson
            self.sheet_id.user_id = self.expense_user_manager
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "You have been assigned to Commercial Travel at New York",
            )
            self.assertIn("Employee", mail_id.body)
        finally:
            self.mail_unlink_enabled()

    def test_02_assigned_activity_more_informations(self):
        try:
            self.mail_unlink_disabled()
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # assign an activity
            activity_id = self.sheet_id.activity_schedule(
                act_type_xmlid="mail.mail_activity_data_todo",
                note="Please check this",
                user_id=self.expense_user_manager.id,
            )
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "Commercial Travel at New York: To Do assigned to you",
            )
            self.assertIn("Employee", mail_id.body)
        finally:
            self.mail_unlink_enabled()
