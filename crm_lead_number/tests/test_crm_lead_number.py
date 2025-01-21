# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.tests.common import TransactionCase


class TestCrmLeadNumber(TransactionCase):

    def _get_next_number(self):
        # should be identical to self.crm_lead._prepare_number()
        return self.sequence.get_next_char(self.sequence.number_next_actual)

    def setUp(self):
        super().setUp()
        self.model_crm = self.env["crm.lead"]
        self.sequence = self.env.ref("crm_lead_number.crm_lead_sequence")
        self.case_lead = self.env.ref("crm.crm_case_1")
        self.case_opportunity = self.env.ref("crm.crm_case_13")
        # brandon.freeman55@example.com
        self.partner_id = self.env.ref("base.res_partner_address_15")

    def test_01_existing_opportunity_number_assign(self):
        lead_ids = self.model_crm.search([("type", "=", "lead")])
        for lead_id in lead_ids:
            self.assertEqual(lead_id.number, "/")
        opportunity_ids = self.model_crm.search([("type", "=", "opportunity")])
        for opportunity_id in opportunity_ids:
            self.assertNotEqual(opportunity_id.number, "/")

    def test_02_new_lead_number_assign(self):
        number = self._get_next_number()
        opportunity_id = self.model_crm.create(
            {
                "name": "Testing number",
                "type": "opportunity",
            }
        )
        self.assertNotEqual(opportunity_id.number, "/")
        self.assertEqual(opportunity_id.number, number)

    def test_03_copy_number_assign(self):
        number = self._get_next_number()
        self.assertEqual(self.case_lead.number, "/")
        lead_copy = self.case_lead.copy()
        self.assertEqual(lead_copy.number, self.case_lead.number)
        self.assertNotEqual(lead_copy.number, number)
        opportunity_copy = self.case_opportunity.copy()
        self.assertNotEqual(opportunity_copy.number, self.case_lead.number)
        self.assertEqual(opportunity_copy.number, number)

    def test_04_name_search(self):
        number = self._get_next_number()
        opportunity_id = self.model_crm.create(
            {
                "name": "InsideVR: XRDevice",
                "type": "opportunity",
                "partner_id": self.partner_id.id,
            }
        )
        # search using computed `search_name`
        lead_ids = self.model_crm.name_search(name="[%s] InsideVR: XRDevice" % (number))
        self.assertEqual(len(lead_ids), 1)
        self.assertEqual(lead_ids[0][0], opportunity_id.id)
        # search using computed `search_name`
        lead_ids = self.model_crm.name_search(name="brandon.freeman55@example.com")
        self.assertEqual(len(lead_ids), 1)
        self.assertEqual(lead_ids[0][0], opportunity_id.id)
