# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.tests.common import TransactionCase


class TestCompanyReport(TransactionCase):

    def setUp(self):
        super().setUp()
        # company model
        self.cm = self.env["res.company"]

    def test_01_(self):
        company_id = self.cm.search([])
        self.assertTrue(company_id.exists())
        # no footer until enabled
        self.assertFalse(company_id.report_bank_footer)
        # check one and only one bank
        partner_bank_id = company_id.bank_ids
        self.assertEqual(len(partner_bank_id), 1)
        partner_bank_id.footer = True
        # ensure no bank record is linked to this partner bank instance
        self.assertFalse(partner_bank_id.bank_id)
        self.assertEqual(company_id.report_bank_footer, "60-16-13 31926819")
        # manually assign an existing bank record
        partner_bank_id.bank_id = self.env.ref("base.bank_bnp")
        self.assertTrue(partner_bank_id.bank_id)
        self.assertEqual(
            company_id.report_bank_footer, "BNP Paribas: 60-16-13 31926819 - GEBABEBB"
        )
