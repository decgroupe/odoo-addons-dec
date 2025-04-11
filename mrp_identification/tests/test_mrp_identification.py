# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase


class TestMrpIdentification(SavepointCase):

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

    def test_10_production_name_get(self):
        # search using name
        name_res = "✨ WH/MO/00001 → 🔧 [FURN_7800] Desk Combination"
        res = self.model_production.name_search(name="00001")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # search using identification name
        res = self.model_production.name_search(name=name_res)
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # set partner to the production
        self.p1.partner_id = self.partner_id
        # search using name
        name_res = (
            "✨ WH/MO/00001 → 🔧 [FURN_7800] Desk Combination "
            "👷 Azure Interior, Brandon Freeman"
        )
        res = self.model_production.name_search(name="00001")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # search using identification name
        res = self.model_production.name_search(name=name_res)
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # set a BoM reference ...
        self.p1.bom_id.code = "#01"
        self.p1.invalidate_cache()
        # ... and retry search using name
        name_res = (
            "✨ WH/MO/00001 → 🔧 [#01] [FURN_7800] Desk Combination "
            "👷 Azure Interior, Brandon Freeman"
        )
        res = self.model_production.name_search(name="00001")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # search using identification name
        res = self.model_production.name_search(name=name_res)
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # set zip to partner
        self.partner_id.zip_id = self.zip_id
        # search using name
        name_res = (
            "✨ WH/MO/00001 → 🔧 [#01] [FURN_7800] Desk Combination "
            "👷 Azure Interior, Brandon Freeman "
            "🗺️ 94538, Fremont, California, United States"
        )
        res = self.model_production.name_search(name="00001")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # search using identification name
        res = self.model_production.name_search(name=name_res)
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # name get should give a standard result (without identification)
        res = self.p1.name_get()
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], "WH/MO/00001")
        # test with name_search context
        res = self.p1.with_context(name_search=True).name_get()
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # confirm the production
        self.p1.action_confirm()
        # search using name
        name_res = (
            "🏳️ WH/MO/00001 → 🔧 [#01] [FURN_7800] Desk Combination "
            "👷 Azure Interior, Brandon Freeman "
            "🗺️ 94538, Fremont, California, United States"
        )
        res = self.model_production.name_search(name="00001")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # search using identification name
        res = self.model_production.name_search(name=name_res)
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # remove icon for this stage
        self.p1.stage_id.emoji = False
        # search using name
        name_res = (
            "WH/MO/00001 → 🔧 [#01] [FURN_7800] Desk Combination "
            "👷 Azure Interior, Brandon Freeman "
            "🗺️ 94538, Fremont, California, United States"
        )
        res = self.model_production.name_search(name="00001")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # search using identification name
        res = self.model_production.name_search(name=name_res)
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)


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
        # search using name
        name_res = "✨ INT/MO/0000X5"
        res = self.model_production.name_search(name="0000X5")
        self.assertEqual(res[0][0], p2.id)
        self.assertEqual(res[0][1], name_res)
        # set partner to the production
        p2.partner_id = self.partner_id
        # search using name
        name_res = "✨ INT/MO/0000X5 → 👷 Azure Interior, Brandon Freeman"
        res = self.model_production.name_search(name="0000X5")
        self.assertEqual(res[0][0], p2.id)
        self.assertEqual(res[0][1], name_res)

    def test_30_search_for(self):
        # search for product
        name_res = "✨ WH/MO/00001 → 🔧 [FURN_7800] Desk Combination"
        res = self.model_production.name_search(name="FURN_7800")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # set a BoM reference
        self.p1.bom_id.code = "#01"
        self.p1.invalidate_cache()
        # and search for BoM reference
        name_res = "✨ WH/MO/00001 → 🔧 [#01] [FURN_7800] Desk Combination"
        res = self.model_production.name_search(name="#01")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        res = self.model_production.name_search(name="Desk Combination")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        # assign partner with city and search for zip
        name_res = (
            "✨ WH/MO/00001 → 🔧 [#01] [FURN_7800] Desk Combination "
            "👷 Azure Interior, Brandon Freeman "
            "🗺️ 94538, Fremont, California, United States"
        )
        self.p1.partner_id = self.partner_id
        self.partner_id.zip_id = self.zip_id
        res = self.model_production.name_search(name="fremont")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        res = self.model_production.name_search(name="94538")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
        res = self.model_production.name_search(name="California")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)

    def test_40_same_bom_code_replacing_product_code(self):
        # set a BoM reference
        self.p1.bom_id.code = "FURN_7800V1"
        self.p1.invalidate_cache()
        # search for product
        name_res = "✨ WH/MO/00001 → 🔧 [FURN_7800V1] Desk Combination"
        res = self.model_production.name_search(name="FURN_7800")
        self.assertEqual(res[0][0], self.p1.id)
        self.assertEqual(res[0][1], name_res)
