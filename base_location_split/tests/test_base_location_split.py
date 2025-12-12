# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

from odoo.tests.common import TransactionCase


class TestBaseLocationSplit(TransactionCase):
    def setUp(self):
        super().setUp()
        self.city0a = self.env["res.city"].create(
            {
                "name": "City0a",
                "zip_ids": [
                    (0, 0, {"name": "53000"}),
                ],
                "country_id": self.env.ref("base.fr").id,
            }
        )
        self.city0b = self.env["res.city"].create(
            {
                "name": "City0b",
                "zip_ids": [
                    (0, 0, {"name": "53000"}),
                    (0, 0, {"name": "53001"}),
                ],
                "country_id": self.env.ref("base.fr").id,
            }
        )
        self.city1 = self.env["res.city"].create(
            {
                "name": "City1",
                "zip_ids": [
                    (0, 0, {"name": "53000"}),
                    (0, 0, {"name": "53001"}),
                    (0, 0, {"name": "44000"}),
                ],
                "country_id": self.env.ref("base.fr").id,
            }
        )
        self.city2 = self.env["res.city"].create(
            {
                "name": "City2",
                "zip_ids": [
                    (0, 0, {"name": "1"}),
                    (0, 0, {"name": "2"}),
                    (0, 0, {"name": "3"}),
                    (0, 0, {"name": "40"}),
                    (0, 0, {"name": "41"}),
                    (0, 0, {"name": "42"}),
                    (0, 0, {"name": "510"}),
                    (0, 0, {"name": "511"}),
                    (0, 0, {"name": "512"}),
                    (0, 0, {"name": "5200"}),
                    (0, 0, {"name": "5201"}),
                    (0, 0, {"name": "5230"}),
                ],
                "country_id": self.env.ref("base.fr").id,
            }
        )

    def test_01_nothing_todo(self):
        cur_city_ids = self.env["res.city"].search([])
        self.assertEqual(len(self.city0a.zip_ids), 1)
        self.city0a.action_split_by_zip()
        self.assertEqual(len(self.city0a.zip_ids), 1)
        new_city_ids = self.env["res.city"].search([]) - cur_city_ids
        self.assertFalse(new_city_ids)

    def test_02_nothing_todo(self):
        cur_city_ids = self.env["res.city"].search([])
        self.assertEqual(len(self.city0b.zip_ids), 2)
        self.city0b.action_split_by_zip()
        self.assertEqual(len(self.city0b.zip_ids), 2)
        new_city_ids = self.env["res.city"].search([]) - cur_city_ids
        self.assertFalse(new_city_ids)

    def test_03_basic_split(self):
        cur_city_ids = self.env["res.city"].search([])
        self.city1.action_split_by_zip()
        self.assertEqual(len(self.city1.zip_ids), 2)
        new_city_ids = self.env["res.city"].search([]) - cur_city_ids
        self.assertEqual(len(new_city_ids), 1)
        city_id = new_city_ids
        self.assertEqual(city_id.name, "City1")
        self.assertEqual(len(city_id.zip_ids), 1)
        self.assertEqual(city_id.zip_ids.name, "44000")

    def test_04_advanced_split(self):
        cur_city_ids = self.env["res.city"].search([])
        self.city2.action_split_by_zip()
        self.assertEqual(len(self.city1.zip_ids), 3)
        new_city_ids = self.env["res.city"].search([]) - cur_city_ids
        self.assertEqual(len(new_city_ids), 4)
        self.assertEqual(set(new_city_ids.mapped("name")), {"City2"})
        self.assertEqual(len(new_city_ids.mapped("zip_ids")), 8)
        # search city with zip "41"
        new1_city_id = self.env["res.city"].search([("zip_ids.name", "=", "41")])
        self.assertEqual(new1_city_id.name, "City2")
        self.assertEqual(len(new1_city_id), 1)
        self.assertEqual(len(new1_city_id.zip_ids), 1)
        self.assertEqual(set(new1_city_id.zip_ids.mapped("name")), {"41"})
        # search city with zip "42"
        new2_city_id = self.env["res.city"].search([("zip_ids.name", "=", "42")])
        self.assertEqual(new2_city_id.name, "City2")
        self.assertEqual(len(new2_city_id), 1)
        self.assertEqual(len(new2_city_id.zip_ids), 1)
        self.assertEqual(set(new2_city_id.zip_ids.mapped("name")), {"42"})
        # search city with zip "510"
        new4_city_id = self.env["res.city"].search([("zip_ids.name", "=", "510")])
        self.assertEqual(new4_city_id.name, "City2")
        self.assertEqual(len(new4_city_id), 1)
        self.assertEqual(len(new4_city_id.zip_ids), 3)
        self.assertEqual(
            set(new4_city_id.zip_ids.mapped("name")), {"510", "511", "512"}
        )
        # search city with zip "5200"
        new5_city_id = self.env["res.city"].search([("zip_ids.name", "=", "5200")])
        self.assertEqual(new5_city_id.name, "City2")
        self.assertEqual(len(new5_city_id), 1)
        self.assertEqual(len(new5_city_id.zip_ids), 3)
        self.assertEqual(
            set(new5_city_id.zip_ids.mapped("name")), {"5200", "5201", "5230"}
        )
