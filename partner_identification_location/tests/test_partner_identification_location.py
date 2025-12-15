# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

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

    def test_01_zip_name_format(self):
        # ensure `base_location_display` module behaviour
        self.assertEqual(self.zip_id.display_name, "75001 London, United Kingdom")

    def test_02_partner_display_name(self):
        partner = self._create_default_partner()
        # Without location
        self._set_partner_company(partner)
        self._set_partner_email(partner)
        self.assertDisplayName(
            partner,
            {"name_search": True},
            "Bob",
            "🏢 Bob → 📧 bob@leponge.com",
        )
        self.assertDisplayName(
            partner,
            {"name_search": True, "idf_no_email": True},
            "Bob",
            "🏢 Bob",
        )
        # Now with location
        self._set_partner_zip_id(partner)
        self.assertDisplayName(
            partner,
            {"name_search": True},
            "Bob",
            "🏢 Bob → (🗺️ 75001 London, United Kingdom) 📧 bob@leponge.com",
        )
        self.assertDisplayName(
            partner,
            {"name_search": True, "idf_no_location": True},
            "Bob",
            "🏢 Bob → 📧 bob@leponge.com",
        )

    def test_03_partner_name_search(self):
        partner = self._create_default_partner()
        self._set_partner_company(partner)
        self._set_partner_email(partner)
        self._set_partner_zip_id(partner)
        self.assertNameSearch(
            partner,
            "Bob",
            "🏢 Bob → (🗺️ 75001 London, United Kingdom) 📧 bob@leponge.com",
        )
        self.assertNameSearch(
            partner,
            "🏢 Bob → (🗺️ 75001 London, United Kingdom) 📧 bob@leponge.com",
            "🏢 Bob → (🗺️ 75001 London, United Kingdom) 📧 bob@leponge.com",
        )
