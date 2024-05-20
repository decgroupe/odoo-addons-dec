# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

import logging

from odoo.addons.mail_extra_notify.tests.common import TestMailExtraNotifyCommon, tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestMailExtraNotifyAccount(TestMailExtraNotifyCommon):

    def setUp(self):
        super().setUp()
        admin = self.env.ref("base.user_admin")
        generic_coa = self.env.ref(
            "l10n_generic_coa.configurable_chart_template", raise_if_not_found=False
        )
        if (
            not admin.company_id.chart_template_id
            or admin.company_id.chart_template_id != generic_coa
        ):
            _logger.info("Generic coa not found.")
            return
        self.invoice_id = self.env.ref("l10n_generic_coa.demo_invoice_followup")
        self.invoice_id.invoice_origin = "SO240123"

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
