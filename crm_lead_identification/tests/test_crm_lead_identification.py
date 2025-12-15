# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.tests.common import TransactionCase


class TestCrmLeadIdentification(TransactionCase):
    def _append_symbol_to_stages(self):
        self.stage_new.name = "✨ " + self.stage_new.name
        self.stage_proposition.name = "✨ " + self.stage_proposition.name
        self.stage_qualified.name = "🏁 " + self.stage_qualified.name
        self.stage_won.name = "🎉 " + self.stage_won.name

    def setUp(self):
        super().setUp()
        self.model_crm = self.env["crm.lead"]
        # tracks stages
        self.stage_new = self.env.ref("crm.stage_lead1")
        self.stage_qualified = self.env.ref("crm.stage_lead2")
        self.stage_proposition = self.env.ref("crm.stage_lead3")
        self.stage_won = self.env.ref("crm.stage_lead4")
        # lead: Quote for 12 Tables
        self.case_13 = self.env.ref("crm.crm_case_13")
        # lead: Club Office More Desks
        self.case_29 = self.env.ref("crm.crm_case_29")
        # opportunity: 5 VP Chairs
        self.case_22 = self.env.ref("crm.crm_case_22")
        # opportunity: Customizable Desk
        self.case_19 = self.env.ref("crm.crm_case_19")
        # opportunity: Balmer Inc: Potential Distributor
        self.case_17 = self.env.ref("crm.crm_case_17")
        # opportunity: Info about services
        self.case_15 = self.env.ref("crm.crm_case_15")
        # enforce numbers for static compare
        self.case_13.number = "SLD/13"
        self.case_29.number = "SLD/29"
        self.case_22.number = "SLD/22"
        self.case_19.number = "SLD/19"
        self.case_17.number = "SLD/17"
        self.case_15.number = "SLD/15"
        self.lead_ids = (
            self.case_13
            + self.case_29
            + self.case_22
            + self.case_19
            + self.case_17
            + self.case_15
        )

    def assertNameSearch(self, lead, name, expected_result):
        self.model_crm.invalidate_model(["display_name"])
        res = self.model_crm.name_search(name=name)
        if not expected_result:
            self.assertFalse(res)
            return
        self.assertEqual(res[0][0], lead.id)
        self.assertEqual(res[0][1], expected_result)

    def assertDisplayName(self, lead, context, normal_name, identification_name):
        self.model_crm.invalidate_model(["display_name"])
        self.assertEqual(lead.display_name, normal_name)
        self.model_crm.invalidate_model(["display_name"])
        self.assertEqual(lead.with_context(**context).display_name, identification_name)

    def test_01_display_name(self):
        self.assertDisplayName(
            self.case_13,
            {"name_search": True},
            "[SLD/13] Quote for 12 Tables",
            "[SLD/13] Quote for 12 Tables",
        )
        self.assertDisplayName(
            self.case_29,
            {"name_search": True},
            "[SLD/29] Club Office More Desks",
            "[SLD/29] Club Office More Desks",
        )
        self.assertDisplayName(
            self.case_22,
            {"name_search": True},
            "[SLD/22] 5 VP Chairs",
            "[SLD/22] 5 VP Chairs → 🏢 Azure Interior",
        )
        self.assertDisplayName(
            self.case_19,
            {"name_search": True},
            "[SLD/19] Customizable Desk",
            "[SLD/19] Customizable Desk → 🏢 Azure Interior",
        )
        self.assertDisplayName(
            self.case_17,
            {"name_search": True},
            "[SLD/17] Balmer Inc: Potential Distributor",
            "[SLD/17] Balmer Inc: Potential Distributor",
        )
        self.assertDisplayName(
            self.case_15,
            {"name_search": True},
            "[SLD/15] Info about services",
            "[SLD/15] Info about services → 🏢 Acme Corporation",
        )

    def test_02_name_search(self):
        res = self.model_crm.name_search(name="Azure Interior")
        res_ids = [x[0] for x in res]
        self.assertIn(self.case_22.id, res_ids)
        self.assertIn(self.case_19.id, res_ids)
        res = self.model_crm.name_search(
            name="[SLD/15] Info about services → 🏢 Acme Corporation"
        )
        res_ids = [x[0] for x in res]
        self.assertEqual(len(res_ids), 1)
        self.assertIn(self.case_15.id, res_ids)
        pass

    def test_03_display_name_with_symbol_in_stage(self):
        self._append_symbol_to_stages()
        # same as test_01
        self.assertDisplayName(
            self.case_13,
            {"name_search": True},
            "[SLD/13] Quote for 12 Tables",
            "✨ [SLD/13] Quote for 12 Tables",
        )
        self.assertDisplayName(
            self.case_29,
            {"name_search": True},
            "[SLD/29] Club Office More Desks",
            "🏁 [SLD/29] Club Office More Desks",
        )
        self.assertDisplayName(
            self.case_22,
            {"name_search": True},
            "[SLD/22] 5 VP Chairs",
            "✨ [SLD/22] 5 VP Chairs → 🏢 Azure Interior",
        )
        self.assertDisplayName(
            self.case_19,
            {"name_search": True},
            "[SLD/19] Customizable Desk",
            "✨ [SLD/19] Customizable Desk → 🏢 Azure Interior",
        )
        self.assertDisplayName(
            self.case_17,
            {"name_search": True},
            "[SLD/17] Balmer Inc: Potential Distributor",
            "🏁 [SLD/17] Balmer Inc: Potential Distributor",
        )
        self.assertDisplayName(
            self.case_15,
            {"name_search": True},
            "[SLD/15] Info about services",
            "🏁 [SLD/15] Info about services → 🏢 Acme Corporation",
        )

    def test_04_name_search_with_symbol_in_stage(self):
        self._append_symbol_to_stages()
        res = self.model_crm.name_search(name="Azure Interior")
        res_ids = [x[0] for x in res]
        self.assertIn(self.case_22.id, res_ids)
        self.assertIn(self.case_19.id, res_ids)
        res = self.model_crm.name_search(
            name="🏁 [SLD/15] Info about services → 🏢 Acme Corporation"
        )
        res_ids = [x[0] for x in res]
        self.assertEqual(len(res_ids), 1)
        self.assertIn(self.case_15.id, res_ids)
