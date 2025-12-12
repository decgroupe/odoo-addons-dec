# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

from odoo.tests.common import TransactionCase


class TestBaseLocationCountCaps(TransactionCase):
    def setUp(self):
        super().setUp()
        self.country = self.env.ref("base.fr")
        self.city1 = self.env["res.city"].create(
            {
                "name": "Abbéville-lès-Conflans",
                "country_id": self.country.id,
            }
        )
        self.city2 = self.env["res.city"].create(
            {
                "name": "Argentré-du-Plessis",
                "country_id": self.country.id,
            }
        )
        # extra space at end
        self.city3 = self.env["res.city"].create(
            {
                "name": "Argentré-du-Plessis ",
                "country_id": self.country.id,
            }
        )
        # separator replace with spaces
        self.city4 = self.env["res.city"].create(
            {
                "name": "Argentré du Plessis",
                "country_id": self.country.id,
            }
        )
        # upper case
        self.city5 = self.env["res.city"].create(
            {
                "name": "ARGENTRÉ DU PLESSIS",
                "country_id": self.country.id,
            }
        )
        # upper case and extra space at start
        self.city6 = self.env["res.city"].create(
            {
                "name": " ARGENTRÉ DU PLESSIS",
                "country_id": self.country.id,
            }
        )
        self.city_ids = (
            self.city1 + self.city2 + self.city3 + self.city4 + self.city5 + self.city6
        )

    def test_01_basic(self):
        self.assertEqual(self.city1.normalized_name, "abbevillelesconflans")
        self.assertEqual(self.city1.caps_count, 2)
        self.assertAlmostEqual(self.city1.caps_ratio, 0.1, delta=0.001)

    def test_02_advanced(self):
        self.assertEqual(self.city2.normalized_name, "argentreduplessis")
        self.assertEqual(self.city3.caps_count, 2)
        self.assertAlmostEqual(self.city2.caps_ratio, 0.117, delta=0.001)
        normalized_name = self.city2.normalized_name

        self.assertEqual(self.city3.normalized_name, normalized_name)
        self.assertEqual(self.city3.caps_count, 2)
        self.assertAlmostEqual(self.city3.caps_ratio, 0.117, delta=0.001)

        self.assertEqual(self.city4.normalized_name, normalized_name)
        self.assertEqual(self.city4.caps_count, 2)
        self.assertAlmostEqual(self.city4.caps_ratio, 0.117, delta=0.001)

        self.assertEqual(self.city5.normalized_name, normalized_name)
        self.assertEqual(self.city5.caps_count, 17)
        self.assertAlmostEqual(self.city5.caps_ratio, 1.0)

        self.assertEqual(self.city6.normalized_name, normalized_name)
        self.assertEqual(self.city6.caps_count, 17)
        self.assertAlmostEqual(self.city6.caps_ratio, 1.0)

        domain = [("id", "in", self.city_ids.ids)]  # search only our city records
        groupby = ["normalized_name"]
        aggregates = ["name:count", "id:recordset"]
        city_group = self.env["res.city"]._read_group(domain, groupby, aggregates)
        self.assertEqual(len(city_group), 2)
        self.assertEqual(city_group[0][0], "abbevillelesconflans")
        self.assertEqual(city_group[0][1], 1)  # count of name
        self.assertEqual(city_group[1][0], "argentreduplessis")
        self.assertEqual(city_group[1][1], 5)  # count of name
