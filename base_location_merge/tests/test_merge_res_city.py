# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import TransactionCase


class TestMergeResCity(TransactionCase):
    def setUp(self):
        super().setUp()
        self.tag_model = self.env["res.city"]
        self.merge_wizard_model = self.env["merge.res.city.wizard"]
        self.group_do_merge = self.env.ref(
            "base_location_merge.res_group_base_location_do_merge"
        )

    def test_01_merge(self):
        # get a first city reference
        c1 = self.env.ref("base_location_merge.demo_montcuq_city")
        # keep current data for future comparison
        c1_data = c1.read()[0]
        # get other city references that will be merged in to the first one
        c2 = self.env.ref("base_location_merge.demo_belmontet_city")
        c3 = self.env.ref("base_location_merge.demo_lebreil_city")
        c4 = self.env.ref("base_location_merge.demo_saintecroix_city")
        c5 = self.env.ref("base_location_merge.demo_valprionde_city")
        # edit some values
        c2.write({})
        c3.write({})
        c4.write({})
        c5.write({})
        # keep current data for future comparison
        c2_data = c2.read()[0]
        c3_data = c3.read()[0]
        c4_data = c4.read()[0]
        c5_data = c5.read()[0]
        # execute first merge (as when can only merge 3 items at a time)
        wizard_id = self.merge_wizard_model.create(
            {
                "object_ids": (c1 + c2 + c3).ids,
                "dst_object_id": c1.id,
            }
        )
        wizard_id.action_merge()
        self.assertTrue(c1.exists())
        self.assertFalse(c2.exists())
        self.assertFalse(c3.exists())
        # execute second merge (as when can only merge 3 items at a time)
        wizard_id = self.merge_wizard_model.create(
            {
                "object_ids": (c1 + c4 + c5).ids,
                "dst_object_id": c1.id,
            }
        )
        wizard_id.action_merge()
        self.assertTrue(c1.exists())
        self.assertFalse(c4.exists())
        self.assertFalse(c5.exists())
        # ---
        self.assertEqual(c1.name, "Montcuq")
        c1.name = "Montcuq-en-Quercy-Blanc"
        c1_new_data = c1.read()[0]
        zip_ids = (
            c1_data["zip_ids"]
            + c2_data["zip_ids"]
            + c3_data["zip_ids"]
            + c4_data["zip_ids"]
            + c5_data["zip_ids"]
        )
        self.assertListEqual(sorted(c1_new_data["zip_ids"]), sorted(zip_ids))
