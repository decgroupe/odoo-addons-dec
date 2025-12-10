# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

from odoo.tests.common import TransactionCase


class TestBaseLocationDisplay(TransactionCase):
    def setUp(self):
        super().setUp()
        self.country = self.env.ref("base.fr")
        self.city = self.env["res.city"].create(
            {
                "name": "Laval",
                "zip_ids": [
                    (0, 0, {"name": "53000"}),
                ],
                "country_id": self.country.id,
            }
        )
        self.state = self.env["res.country.state"].create(
            {
                "name": "Pays de la Loire",
                "code": "52dc2b4632",
                "country_id": self.country.id,
            }
        )

    def test_01_name_format(self):
        self.assertEqual(
            self.city.zip_ids[0].display_name,
            "53000 Laval, France",
        )
        # assign state
        self.city.state_id = self.state
        self.assertEqual(
            self.city.zip_ids[0].display_name,
            "53000 Laval, Pays de la Loire, France",
        )
        self.country.hide_state = True
        self.assertEqual(
            self.city.zip_ids[0].display_name,
            "53000 Laval, France",
        )
