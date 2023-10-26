# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestMrpMail(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.production_model = self.env["mrp.production"]
        self.product1 = self.env.ref("product.product_product_6")
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.production_user = new_test_user(
            self.env,
            login="mrp_acl-production_user",
            groups="mrp.group_mrp_user",
            context=ctx,
        )

    def test_01_autocreate_alias(self):
        production_id = self.production_model.with_user(self.production_user).create(
            {
                "name": "WH/MO/12345678",
                "product_id": self.product1.id,
                "product_uom_id": self.product1.uom_id.id,
            }
        )
        self.assertEqual(production_id.alias_name, "whmo12345678")
        self.assertEqual(production_id.alias_force_thread_id, production_id.id)

    def test_02_set_alias_later(self):
        production_id = (
            self.production_model.with_user(self.production_user)
            .with_context(no_mail_alias_autocreate=True)
            .create(
                {
                    "name": "WH/MO/12345678",
                    "product_id": self.product1.id,
                    "product_uom_id": self.product1.uom_id.id,
                }
            )
        )
        self.assertEqual(production_id.alias_name, False)
        production_id.name = "WH/MO/87654321"
        self.assertEqual(production_id.alias_name, "whmo87654321")
        self.assertEqual(production_id.alias_force_thread_id, production_id.id)
        production_id.alias_name = False
        production_id.name = "WH/MO/87654321/alt"
        self.assertEqual(production_id.alias_name, "whmo87654321alt")
        self.assertEqual(production_id.alias_force_thread_id, production_id.id)
        print(1)
