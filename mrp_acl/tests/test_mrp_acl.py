# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase
from odoo.exceptions import AccessError


class TestProjectAcl(SavepointCase):
    """ """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.production_model = cls.env["mrp.production"]
        cls.bom_model = cls.env["mrp.bom"]
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.production_user = new_test_user(
            cls.env,
            login="mrp_acl-production_user",
            groups="mrp.group_mrp_user",
            context=ctx,
        )
        cls.production_manager = new_test_user(
            cls.env,
            login="mrp_acl-production_manager",
            groups="mrp.group_mrp_manager",
            context=ctx,
        )
        cls.production_supermanager = new_test_user(
            cls.env,
            login="mrp_acl-production_supermanager",
            groups="mrp_acl.group_mrp_supermanager",
            context=ctx,
        )
        cls.product1 = cls.env.ref("product.product_product_6")
        cls.bom1 = cls.bom_model.create(
            {
                "code": "bom1",
                "product_tmpl_id": cls.product1.product_tmpl_id.id,
                "product_id": cls.product1.id,
            }
        )

    def test_01_create_production_as_production_user(self):
        with self.assertRaisesRegex(AccessError, r"Super-Manager"):
            self.bom1.with_user(self.production_user).write({"code": "123"})
        # in bypass mode, the standard access error should be raised because a
        # production user do not have rights to edit BoM
        with self.assertRaisesRegex(AccessError, r"Manufacturing\/Administrator"):
            self.bom1.with_user(self.production_user).with_context(
                bypass_supermanager_check=True
            ).write({"code": "123"})

    def test_02_create_production_as_production_manager(self):
        with self.assertRaisesRegex(AccessError, r"Super-Manager"):
            self.bom1.with_user(self.production_manager).write({"code": "123"})
        self.bom1.with_user(self.production_manager).with_context(
            bypass_supermanager_check=True
        ).write({"code": "123"})
        self.assertEqual(self.bom1.code, "123")

    def test_03_create_production_as_production_supermanager(self):
        self.bom1.with_user(self.production_supermanager).write({"code": "123"})
        self.assertEqual(self.bom1.code, "123")

    def test_04_create_production_as_production_supermanager_with_bypass(self):
        self.bom1.with_user(self.production_supermanager).with_context(
            bypass_supermanager_check=True
        ).write({"code": "123"})
        self.assertEqual(self.bom1.code, "123")
