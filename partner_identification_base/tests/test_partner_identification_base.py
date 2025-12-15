# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2024

from odoo.addons.partner_identification_base.tests.common import (
    TestPartnerIdentificationBaseCommon,
)


class TestPartnerIdentificationBase(TestPartnerIdentificationBaseCommon):
    def setUp(self):
        super().setUp()

    def test_01_partner_display_name(self):
        partner = self._create_default_partner()
        self.assertDisplayName(
            partner,
            {"name_search": True},
            "Bob",
            "👷 Bob",
        )
        self._set_partner_company(partner)
        self.assertDisplayName(
            partner,
            {"name_search": True},
            "Bob",
            "🏢 Bob",
        )
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
        self._set_partner_city(partner)
        self.assertDisplayName(
            partner,
            {"name_search": True},
            "Bob",
            "🏢 Bob → (London) 📧 bob@leponge.com",
        )
        self._set_partner_zip(partner)
        self.assertDisplayName(
            partner,
            {"name_search": True},
            "Bob",
            "🏢 Bob → (75001 London) 📧 bob@leponge.com",
        )

        self._set_partner_city(partner, False)
        self.assertDisplayName(
            partner,
            {"name_search": True},
            "Bob",
            "🏢 Bob → (75001) 📧 bob@leponge.com",
        )
        self.assertDisplayName(
            partner,
            {"name_search": True, "idf_no_location": True},
            "Bob",
            "🏢 Bob → 📧 bob@leponge.com",
        )

    def test_02_partner_name_search(self):
        partner = self._create_default_partner()
        self.assertNameSearch(
            partner,
            "Bob",
            "👷 Bob",
        )
        self.assertNameSearch(
            partner,
            "👷 Bob",
            "👷 Bob",
        )
        self.assertNameSearch(
            partner,
            "🌝 Bob",
            False,
        )
        # Set as company
        self._set_partner_company(partner)
        self.assertNameSearch(
            partner,
            "Bob",
            "🏢 Bob",
        )
        self.assertNameSearch(
            partner,
            "🏢 Bob",
            "🏢 Bob",
        )
        self.assertNameSearch(
            partner,
            "🌝 Bob",
            False,
        )
        # Add email
        self._set_partner_email(partner)
        self.assertNameSearch(
            partner,
            "Bob",
            "🏢 Bob → 📧 bob@leponge.com",
        )
        self.assertNameSearch(
            partner,
            "🏢 Bob → 📧 bob@leponge.com",
            "🏢 Bob → 📧 bob@leponge.com",
        )
        # Add city
        self._set_partner_city(partner)
        self.assertNameSearch(
            partner,
            "Bob",
            "🏢 Bob → (London) 📧 bob@leponge.com",
        )
        self.assertNameSearch(
            partner,
            "🏢 Bob → (London) 📧 bob@leponge.com",
            "🏢 Bob → (London) 📧 bob@leponge.com",
        )
        # Add zip
        self._set_partner_zip(partner)
        self.assertNameSearch(
            partner,
            "Bob",
            "🏢 Bob → (75001 London) 📧 bob@leponge.com",
        )
        self.assertNameSearch(
            partner,
            "🏢 Bob → (75001 London) 📧 bob@leponge.com",
            "🏢 Bob → (75001 London) 📧 bob@leponge.com",
        )
        # Remove city
        self._set_partner_city(partner, False)
        self.assertNameSearch(
            partner,
            "Bob",
            "🏢 Bob → (75001) 📧 bob@leponge.com",
        )
        self.assertNameSearch(
            partner,
            "🏢 Bob → (75001) 📧 bob@leponge.com",
            "🏢 Bob → (75001) 📧 bob@leponge.com",
        )
