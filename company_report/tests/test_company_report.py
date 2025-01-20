# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.tests.common import TransactionCase


class TestCompanyReport(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company_id = self.env.ref("base.main_company")
        self.assertTrue(self.company_id.exists())

    def test_01_footer_format(self):
        # no footer until enabled
        self.assertFalse(self.company_id.report_bank_footer)
        # check one and only one bank
        partner_bank_id = self.company_id.bank_ids
        self.assertEqual(len(partner_bank_id), 1)
        partner_bank_id.footer = True
        # ensure no bank record is linked to this partner bank instance
        self.assertFalse(partner_bank_id.bank_id)
        self.assertEqual(self.company_id.report_bank_footer, "60-16-13 31926819")
        # manually assign an existing bank record
        partner_bank_id.bank_id = self.env.ref("base.bank_bnp")
        self.assertTrue(partner_bank_id.bank_id)
        self.assertEqual(
            self.company_id.report_bank_footer,
            "BNP Paribas: 60-16-13 31926819 - GEBABEBB",
        )
