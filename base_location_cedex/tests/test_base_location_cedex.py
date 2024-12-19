# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

from odoo.tests.common import TransactionCase
from odoo.tests import Form


class TestBaseLocationCedex(TransactionCase):

    def setUp(self):
        super().setUp()
        self.country = self.env.ref("base.fr")
        self.city = self.env["res.city"].create(
            {
                "name": "Laval",
                "zip_ids": [
                    (0, 0, {"name": "53000", "cedex": "Cedex"}),
                    (0, 0, {"name": "53001", "cedex": "CEDEX"}),
                    (0, 0, {"name": "53101", "cedex": "1"}),
                    (0, 0, {"name": "53102", "cedex": "01"}),
                    (0, 0, {"name": "53103", "cedex": "02"}),
                    (0, 0, {"name": "53200", "cedex": "-"}),
                    (0, 0, {"name": "53300", "cedex": False}),
                ],
                "country_id": self.country.id,
            }
        )
        # keep track of created zips
        self.zip1 = self.env["res.city.zip"].search([("name", "=", "53000")])
        self.zip2 = self.env["res.city.zip"].search([("name", "=", "53001")])
        self.zip3 = self.env["res.city.zip"].search([("name", "=", "53101")])
        self.zip4 = self.env["res.city.zip"].search([("name", "=", "53102")])
        self.zip5 = self.env["res.city.zip"].search([("name", "=", "53103")])
        self.zip6 = self.env["res.city.zip"].search([("name", "=", "53200")])
        self.zip7 = self.env["res.city.zip"].search([("name", "=", "53300")])

    def test_01_format_zip_name_with_cedex(self):
        self.assertEqual(self.zip1.display_name, "53000 Laval Cedex, France")
        self.assertEqual(self.zip2.display_name, "53001 Laval Cedex, France")
        self.assertEqual(self.zip3.display_name, "53101 Laval Cedex 1, France")
        self.assertEqual(self.zip4.display_name, "53102 Laval Cedex 01, France")
        self.assertEqual(self.zip5.display_name, "53103 Laval Cedex 02, France")
        self.assertEqual(self.zip6.display_name, "53200 Laval Cedex, France")
        self.assertEqual(self.zip7.display_name, "53300 Laval, France")

    def test_02_partner_city_cedex(self):
        """Test that partner data is filled accodingly"""
        partner1 = Form(self.env["res.partner"])
        partner1.zip_id = self.zip4
        self.assertEqual(partner1.zip, "53102")
        self.assertEqual(partner1.city, "Laval Cedex 01")
