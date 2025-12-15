# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2024

from odoo.tests.common import TransactionCase


class TestPartnerIdentificationBaseCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_partner = cls.env["res.partner"]

    def _create_default_partner(self):
        return self.model_partner.create({"name": "Bob"})

    def _set_partner_company(self, partner):
        partner.is_company = True

    def _set_partner_email(self, partner):
        partner.email = "bob@leponge.com"

    def _set_partner_city(self, partner, value=None):
        if value is not None:
            partner.city = value
        else:
            partner.city = "London"

    def _set_partner_zip(self, partner):
        partner.zip = "75001"

    def assertDisplayName(self, partner, context, normal_name, identification_name):
        self.model_partner.invalidate_model(["display_name"])
        self.assertEqual(partner.display_name, normal_name)
        self.model_partner.invalidate_model(["display_name"])
        self.assertEqual(
            partner.with_context(**context).display_name, identification_name
        )

    def assertNameSearch(self, partner, name, expected_result):
        self.model_partner.invalidate_model(["display_name"])
        res = self.model_partner.name_search(name=name)
        if not expected_result:
            self.assertFalse(res)
            return
        self.assertEqual(res[0][0], partner.id)
        self.assertEqual(res[0][1], expected_result)
