# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import TransactionCase


class TestMergeResCityZip(TransactionCase):
    def setUp(self):
        super().setUp()
        self.tag_model = self.env["res.city.zip"]
        self.merge_wizard_model = self.env["merge.res.city.zip.wizard"]
        self.group_do_merge = self.env.ref(
            "base_location_merge.res_group_base_location_do_merge"
        )

    def test_01_merge(self):
        city = self.env.ref("base_location_merge.demo_lemans_city")
        # get zip references
        z1 = self.env.ref("base_location_merge.demo_lemans_72000_zip")
        # keep current data for future comparison
        z1_data = z1.read()[0]
        # get other zip references that will be merged in to the first one
        z2 = self.env.ref("base_location_merge.demo_lemans_72002_zip")
        z3 = self.env.ref("base_location_merge.demo_lemans_72003_zip")
        # edit some values
        z2.write({})
        z3.write({})
        # keep current data for future comparison
        z2_data = z2.read()[0]
        z3_data = z3.read()[0]
        # execute merge
        wizard_id = self.merge_wizard_model.create(
            {
                "object_ids": (z1 + z2 + z3).ids,
                "dst_object_id": z1.id,
            }
        )
        wizard_id.action_merge()
        self.assertTrue(z1.exists())
        self.assertFalse(z2.exists())
        self.assertFalse(z3.exists())
        z1_new_data = z1.read()[0]
        # check values
        self.assertEqual(z1_data["name"], z1_new_data["name"])
        self.assertEqual(z1_data["city_id"], z1_new_data["city_id"])
        # check only remaining zips (72000 and 72100)
        self.assertEqual(len(city.zip_ids), 2)
        self.assertIn("72000", city.zip_ids.mapped("name"))
        self.assertIn("72100", city.zip_ids.mapped("name"))
