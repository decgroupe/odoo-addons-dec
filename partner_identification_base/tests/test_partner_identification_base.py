# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2024

from odoo.tests import new_test_user
from odoo.addons.partner_identification_base.tests.common import (
    TestPartnerIdentificationBaseCommon,
)


class TestPartnerIdentificationBase(TestPartnerIdentificationBaseCommon):

    def setUp(self):
        super().setUp()

    def test_01_partner_name_get(self):
        partner = self._create_default_partner()
        ctx = {"name_search": True}
        self.assertEqual(partner.name_get()[0][1], "Bob")
        self.assertEqual(
            partner.with_context(**ctx).name_get()[0][1],
            "👷 Bob",
        )
        self._set_partner_company(partner)
        self.assertEqual(partner.name_get()[0][1], "Bob")
        self.assertEqual(
            partner.with_context(**ctx).name_get()[0][1],
            "🏢 Bob",
        )
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
        self._set_partner_city(partner)
        self.assertEqual(
            partner.with_context(**ctx).name_get()[0][1],
            "🏢 Bob → (London) 📧 bob@leponge.com",
        )
        self._set_partner_zip(partner)
        self.assertEqual(
            partner.with_context(**ctx).name_get()[0][1],
            "🏢 Bob → (75001 London) 📧 bob@leponge.com",
        )
        self._set_partner_city(partner, False)
        self.assertEqual(
            partner.with_context(**ctx).name_get()[0][1],
            "🏢 Bob → (75001) 📧 bob@leponge.com",
        )
        self.assertEqual(
            partner.with_context(**ctx, idf_no_location=True).name_get()[0][1],
            "🏢 Bob → 📧 bob@leponge.com",
        )

    def test_02_partner_name_search(self):
        partner = self._create_default_partner()
        res = self.model_partner.name_search(name="Bob")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "👷 Bob")
        res = self.model_partner.name_search(name="👷 Bob")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "👷 Bob")
        res = self.model_partner.name_search(name="🌝 Bob")
        self.assertFalse(res)
        self._set_partner_company(partner)
        res = self.model_partner.name_search(name="Bob")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "🏢 Bob")
        res = self.model_partner.name_search(name="🏢 Bob")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "🏢 Bob")
        self._set_partner_email(partner)
        res = self.model_partner.name_search(name="Bob")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "🏢 Bob → 📧 bob@leponge.com")
        res = self.model_partner.name_search(name="🏢 Bob → 📧 bob@leponge.com")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "🏢 Bob → 📧 bob@leponge.com")
        self._set_partner_city(partner)
        res = self.model_partner.name_search(name="Bob")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "🏢 Bob → (London) 📧 bob@leponge.com")
        res = self.model_partner.name_search(
            name="🏢 Bob → (London) 📧 bob@leponge.com"
        )
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "🏢 Bob → (London) 📧 bob@leponge.com")
        self._set_partner_zip(partner)
        res = self.model_partner.name_search(name="Bob")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "🏢 Bob → (75001 London) 📧 bob@leponge.com")
        res = self.model_partner.name_search(
            name="🏢 Bob → (75001 London) 📧 bob@leponge.com"
        )
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "🏢 Bob → (75001 London) 📧 bob@leponge.com")
        self._set_partner_city(partner, False)
        res = self.model_partner.name_search(name="Bob")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "🏢 Bob → (75001) 📧 bob@leponge.com")
        res = self.model_partner.name_search(name="🏢 Bob → (75001) 📧 bob@leponge.com")
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], "🏢 Bob → (75001) 📧 bob@leponge.com")
