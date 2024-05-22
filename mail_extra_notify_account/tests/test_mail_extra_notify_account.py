# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo.addons.mail_extra_notify.tests.common import TestMailExtraNotifyCommon, tagged


@tagged("post_install", "-at_install")
class TestMailExtraNotifyAccount(TestMailExtraNotifyCommon):

    def setUp(self):
        super().setUp()
        journal_id = self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )
        type_receivable = self.env.ref("account.data_account_type_receivable")
        type_revenue = self.env.ref("account.data_account_type_revenue")
        receivable_account = self.env["account.account"].search(
            [
                ("user_type_id", "=", type_receivable.id),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        revenue_account = self.env["account.account"].search(
            [
                ("user_type_id", "=", type_revenue.id),
                ("company_id", "=", self.env.company.id),
            ],
            limit=1,
        )
        self.invoice_id = self.env["account.move"].create(
            {
                "invoice_origin": "SO240123",
                "journal_id": journal_id.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line1",
                            "debit": 100.0,
                            "account_id": receivable_account.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "line2",
                            "credit": 100.0,
                            "account_id": revenue_account.id,
                        },
                    ),
                ],
            }
        )

    def test_01_assigned_invoice_more_informations(self):
        try:
            self.mail_unlink_disabled()
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # set salesperson
            self.invoice_id.user_id = self.user1
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "You have been assigned to %s" % self.invoice_id.name_get()[0][1],
            )
            self.assertIn("Origin", mail_id.body)
            self.assertIn("Status", mail_id.body)
            self.assertIn("Total", mail_id.body)
        finally:
            self.mail_unlink_enabled()

    def test_02_assigned_activity_more_informations(self):
        try:
            self.mail_unlink_disabled()
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # assign an activity
            activity_id = self.invoice_id.activity_schedule(
                act_type_xmlid="mail.mail_activity_data_todo",
                note="Please check this",
                user_id=self.user1.id,
            )
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "%s: To Do assigned to you" % self.invoice_id.name_get()[0][1],
            )
            self.assertIn("Origin", mail_id.body)
            self.assertIn("Status", mail_id.body)
            self.assertIn("Total", mail_id.body)
        finally:
            self.mail_unlink_enabled()

    def test_03_assigned_draft_invoice_more_informations(self):
        try:
            self.mail_unlink_disabled()
            draft_invoice_id = self.env["account.move"].create(
                {  # Azure Interior
                    "partner_id": self.env.ref("base.res_partner_12").id,
                    # Azure Interior, Brandon Freeman
                    "partner_shipping_id": self.env.ref(
                        "base.res_partner_address_15"
                    ).id,
                }
            )
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # set salesperson
            draft_invoice_id.user_id = self.user1
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "You have been assigned to Draft Entry %s" % (draft_invoice_id.name),
            )
            self.assertIn("Delivery Address", mail_id.body)  # partner_shipping_id
            self.assertIn("Status", mail_id.body)
            self.assertIn("Total", mail_id.body)
        finally:
            self.mail_unlink_enabled()
