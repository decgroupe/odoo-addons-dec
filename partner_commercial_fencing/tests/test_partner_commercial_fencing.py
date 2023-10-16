# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import TransactionCase


class TestPartnerCommercialFencing(TransactionCase):
    def setUp(self):
        super().setUp()

    def _create_partner(self, name, vals={}):
        Partner = self.env["res.partner"]
        if not "name" in vals:
            vals["name"] = name
        return Partner.create(vals)

    def test_01_commercial_partner_inheriting(self):
        capule_corp = self._create_partner(
            name="Capsule Corp.",
            vals={"is_company": True},
        )
        seller_1 = self._create_partner(
            name="Seller 1", vals={"parent_id": capule_corp.id}
        )
        sub_seller_1a = self._create_partner(
            name="Sub-Seller 1a", vals={"parent_id": seller_1.id}
        )
        sub_seller_1b = self._create_partner(
            name="Sub-Seller 1b", vals={"parent_id": seller_1.id}
        )
        seller_2 = self._create_partner(
            name="Seller 2",
            vals={
                "parent_id": capule_corp.id,
                "inherit_commercial_partner": False,
            },
        )
        sub_seller_2a = self._create_partner(
            name="Sub-Seller 2a", vals={"parent_id": seller_2.id}
        )
        sub_seller_2b = self._create_partner(
            name="Sub-Seller 2b", vals={"parent_id": seller_2.id}
        )

        # check that commercial partner works like builtin when inherit is not set
        self.assertEqual(seller_1.commercial_partner_id, capule_corp)
        self.assertEqual(sub_seller_1a.commercial_partner_id, capule_corp)
        self.assertEqual(sub_seller_1b.commercial_partner_id, capule_corp)
        # check that commercial partner is correctly overrriden
        self.assertEqual(seller_2.commercial_partner_id, seller_2)
        self.assertEqual(sub_seller_2a.commercial_partner_id, seller_2)
        self.assertEqual(sub_seller_2b.commercial_partner_id, seller_2)
        # check that original commercial partner can still be accessed if needed
        self.assertEqual(seller_2.unfenced_commercial_partner_id, capule_corp)
        self.assertEqual(sub_seller_2a.unfenced_commercial_partner_id, capule_corp)
        self.assertEqual(sub_seller_2b.unfenced_commercial_partner_id, capule_corp)
