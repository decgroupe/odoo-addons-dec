# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2024

from odoo.tests.common import SavepointCase


class TestPartnerIdentificationBaseCommon(SavepointCase):

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
        if not value is None:
            partner.city = value
        else:
            partner.city = "London"

    def _set_partner_zip(self, partner):
        partner.zip = "75001"
