# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestMrpIdentification(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_production = cls.env["mrp.production"]
        cls.model_bom = cls.env["mrp.bom"]
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.user = new_test_user(
            cls.env,
            login="mrp_identification-user",
            groups="base.group_user",
            context=ctx,
        )

    def setUp(self):
        super().setUp()
        # WH/MO/00001: [FURN_7800] Desk Combination
        self.p1 = self.env.ref("mrp.mrp_production_1")
        self.assertEqual(self.p1.state, "confirmed")
        # WH/MO/00002: [FURN_9666] Table
        self.p2 = self.env.ref("mrp.mrp_production_3")
        self.assertEqual(self.p2.state, "draft")
        # Azure Interior, Brandon Freeman
        self.partner_id = self.env.ref("base.res_partner_address_15")
        # create city and zip record from Azure Interior address
        self.city_id = self.env["res.city"].create(
            {
                "name": self.partner_id.city,
                "country_id": self.partner_id.country_id.id,
                "state_id": self.partner_id.state_id.id,
            }
        )
        self.zip_id = self.env["res.city.zip"].create(
            {
                "name": self.partner_id.zip,
                "city_id": self.city_id.id,
            }
        )

    def assertNameSearchEqual(self, production, name, expected_result):
        self.model_production.invalidate_model(["display_name"])
        res = self.model_production.name_search(name=name)
        if not expected_result:
            self.assertFalse(res)
            return
        try:
            self.assertEqual(res[0][0], production.id)
            self.assertEqual(res[0][1], expected_result)
        except IndexError:
            self.fail(
                f"Expected to find a production with name_search '{name}' "
                f"but found {res}.\n"
                f"Production is '{production.display_name}'"
            )

    def assertNameSearchRegex(self, production, name, pattern):
        self.model_production.invalidate_model(["display_name"])
        res = self.model_production.name_search(name=name)
        if not pattern:
            self.assertFalse(res)
            return
        try:
            self.assertEqual(res[0][0], production.id)
            self.assertRegex(res[0][1], pattern)
        except IndexError:
            self.fail(
                f"Expected to find a production with name_search '{name}' "
                f"but found {res}.\n"
                f"Production is '{production.display_name}'"
            )

    def assertDisplayName(self, production, context, normal_name, identification_name):
        self.model_production.invalidate_model(["display_name"])
        self.assertEqual(production.display_name, normal_name)
        self.model_production.invalidate_model(["display_name"])
        self.assertEqual(
            production.with_context(**context).display_name, identification_name
        )

    def test_10_production_display_name(self):
        # search using name
        self.assertNameSearchEqual(
            self.p2,
            "00002",
            "✨ WH/MO/00002 → 🔧 [FURN_9666] Table",
        )
        # search using identification name
        self.assertNameSearchEqual(
            self.p2,
            "✨ WH/MO/00002 → 🔧 [FURN_9666] Table",
            "✨ WH/MO/00002 → 🔧 [FURN_9666] Table",
        )
        # set partner to the production
        self.p2.partner_id = self.partner_id
        # search using name
        self.assertNameSearchEqual(
            self.p2,
            "00002",
            "✨ WH/MO/00002 → 🔧 [FURN_9666] Table "
            "👷 Azure Interior, Brandon Freeman",
        )
        # search using identification name
        self.assertNameSearchEqual(
            self.p2,
            "✨ WH/MO/00002 → 🔧 [FURN_9666] Table "
            "👷 Azure Interior, Brandon Freeman",
            "✨ WH/MO/00002 → 🔧 [FURN_9666] Table "
            "👷 Azure Interior, Brandon Freeman",
        )
        # set a BoM reference ...
        self.p2.bom_id.code = "#01"
        self.p2.invalidate_recordset()
        # ... and retry search using name
        self.assertNameSearchEqual(
            self.p2,
            "00002",
            "✨ WH/MO/00002 → 🔧 [#01] [FURN_9666] Table "
            "👷 Azure Interior, Brandon Freeman",
        )
        # search using identification name
        self.assertNameSearchEqual(
            self.p2,
            "✨ WH/MO/00002 → 🔧 [#01] [FURN_9666] Table "
            "👷 Azure Interior, Brandon Freeman",
            "✨ WH/MO/00002 → 🔧 [#01] [FURN_9666] Table "
            "👷 Azure Interior, Brandon Freeman",
        )
        # set zip to partner
        self.partner_id.zip_id = self.zip_id
        # search using name
        pattern = (
            r"✨ WH/MO/00002 → 🔧 \[#01\] \[FURN_9666\] Table "
            r"👷 Azure Interior, Brandon Freeman "
            r"🗺️ 94538,? Fremont, California, United States"
        )
        self.assertNameSearchRegex(self.p2, "00002", pattern)
        # search using identification name
        self.assertNameSearchRegex(self.p2, pattern, pattern)
        # name get should give a standard result (without identification)
        self.p2.invalidate_recordset()
        self.assertEqual(self.p2.display_name, "WH/MO/00002")
        # test with name_search context
        p2_with_context = self.p2.with_context(name_search=True)
        p2_with_context.invalidate_recordset()
        self.assertRegex(p2_with_context.display_name, pattern)
        # confirm the production
        self.p2.action_confirm()
        self.assertEqual(self.p2.state, "confirmed")
        # set custom stage symbol (could be different because of extended stage list
        # by other modules like mrp_supply_progress) and check the name_search result
        # contains it
        self.p2.stage_id.symbol = "💓"
        # search using name
        pattern = (
            r"💓 WH/MO/00002 → 🔧 \[#01\] \[FURN_9666\] Table "
            r"👷 Azure Interior, Brandon Freeman "
            r"🗺️ 94538,? Fremont, California, United States"
        )
        self.assertNameSearchRegex(self.p2, "00002", pattern)
        # search using identification name
        self.assertNameSearchRegex(self.p2, pattern, pattern)
        # remove icon for this stage
        self.p2.stage_id.symbol = False
        # search using name
        pattern = (
            r"WH/MO/00002 → 🔧 \[#01\] \[FURN_9666\] Table "
            r"👷 Azure Interior, Brandon Freeman "
            r"🗺️ 94538,? Fremont, California, United States"
        )
        self.assertNameSearchRegex(self.p2, "00002", pattern)
        # search using identification name
        self.assertNameSearchRegex(self.p2, pattern, pattern)

    def test_20_production_without_bom_name_get(self):
        p2 = self.env["mrp.production"].create(
            {
                "name": "INT/MO/0000X5",
                "product_id": self.p1.product_id.id,
                "product_uom_id": self.p1.product_id.uom_id.id,
                "product_qty": 1,
                "bom_id": False,
            }
        )
        # force stage to draft because other modules may override stage computation
        # behavior (auto-complete production order when BoM is not set)
        p2.stage_id = self.env.ref("mrp_stage.stage_draft")
        # search using name
        name_res = "✨ INT/MO/0000X5"
        res = self.model_production.name_search(name="0000X5")
        self.assertEqual(res[0][0], p2.id)
        self.assertRegex(res[0][1], name_res)
        # set partner to the production
        p2.partner_id = self.partner_id
        # search using name
        name_res = "✨ INT/MO/0000X5 → 👷 Azure Interior, Brandon Freeman"
        res = self.model_production.name_search(name="0000X5")
        self.assertEqual(res[0][0], p2.id)
        self.assertRegex(res[0][1], name_res)

    def test_30_search_for(self):
        # search for product
        name_res = "🏳️ WH/MO/00001 → 🔧 [FURN_7800] Desk Combination"
        res = self.model_production.name_search(name="FURN_7800")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # set a BoM reference
        self.p1.bom_id.code = "#01"
        self.p1.invalidate_recordset()
        # and search for BoM reference
        name_res = "🏳️ WH/MO/00001 → 🔧 [#01] [FURN_7800] Desk Combination"
        res = self.model_production.name_search(name="#01")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        res = self.model_production.name_search(name="Desk Combination")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # assign partner with city and search for zip
        name_res = (
            r"🏳️ WH/MO/00001 → 🔧 \[#01\] \[FURN_7800\] Desk Combination "
            r"👷 Azure Interior, Brandon Freeman "
            r"🗺️ 94538,? Fremont, California, United States"
        )
        self.p1.partner_id = self.partner_id
        self.partner_id.zip_id = self.zip_id
        res = self.model_production.name_search(name="fremont")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertRegex(res[0][1], name_res)
        res = self.model_production.name_search(name="94538")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertRegex(res[0][1], name_res)
        res = self.model_production.name_search(name="California")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertRegex(res[0][1], name_res)

    def test_40_same_bom_code_replacing_product_code(self):
        # set a BoM reference
        self.p1.bom_id.code = "FURN_7800V1"
        self.p1.invalidate_recordset()
        # search for product
        name_res = "🏳️ WH/MO/00001 → 🔧 [FURN_7800V1] Desk Combination"
        res = self.model_production.name_search(name="FURN_7800")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
