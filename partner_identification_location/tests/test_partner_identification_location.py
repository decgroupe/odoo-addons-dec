# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.tests.common import TransactionCase
from odoo.addons.partner_identification_base.tests.common import (
    TestPartnerIdentificationBaseCommon,
)


class TestPartnerIdentificationLocation(TestPartnerIdentificationBaseCommon):

    def setUp(self):
        super().setUp()
        self.city_id = self.env["res.city"].create(
            {
                "name": "London",
                "country_id": self.env.ref("base.uk").id,
            }
        )
        self.zip_id = self.env["res.city.zip"].create(
            {
                "name": "75001",
                "city_id": self.city_id.id,
            }
        )

    def _set_partner_zip_id(self, partner):
        partner.zip_id = self.zip_id

    def test_01_partner_name_get(self):
        partner = self._create_default_partner()
        ctx = {"name_search": True}
        self._set_partner_company(partner)
        self._set_partner_email(partner)
        self.assertEqual(partner.name_get()[0][1], "Bob")
        self.assertEqual(
            partner.with_context(**ctx).name_get()[0][1],
            "🏢 Bob → 📧 bob@leponge.com",
        )
        self.assertEqual(
            partner.with_context(**ctx, idf_no_email=True).name_get()[0][1],
            "🏢 Bob",
        )
        self._set_partner_zip_id(partner)
        self.assertEqual(
            partner.with_context(**ctx).name_get()[0][1],
            "🏢 Bob → (🗺️ 75001, London, United Kingdom) 📧 bob@leponge.com",
        )
        self.assertEqual(
            partner.with_context(**ctx, idf_no_location=True).name_get()[0][1],
            "🏢 Bob → 📧 bob@leponge.com",
        )

    def test_02_partner_name_search(self):
        partner = self._create_default_partner()
        self._set_partner_company(partner)
        self._set_partner_email(partner)
        self._set_partner_zip_id(partner)
        res = self.model_partner.name_search(name="Bob")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(
            res[0][1], "🏢 Bob → (🗺️ 75001, London, United Kingdom) 📧 bob@leponge.com"
        )
        res = self.model_partner.name_search(
            name="🏢 Bob → (🗺️ 75001, London, United Kingdom) 📧 bob@leponge.com"
        )
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(
            res[0][1], "🏢 Bob → (🗺️ 75001, London, United Kingdom) 📧 bob@leponge.com"
        )
