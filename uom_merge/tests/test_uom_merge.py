# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.exceptions import AccessDenied
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestUomMerge(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.uom_model = self.env["uom.uom"]
        self.merge_uom_wizard_model = self.env["merge.uom.uom.wizard"]
        self.group_do_merge = self.env.ref("uom_merge.res_group_do_merge")
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.user = new_test_user(
            self.env,
            login="uom_merge-user",
            groups="base.group_user",
            context=ctx,
        )

    def _create_uom(self, name, category_id, uom_type="smaller", factor=1000.0):
        return self.uom_model.create(
            {
                "name": name,
                "category_id": category_id,
                "uom_type": uom_type,
                "factor": factor,
            }
        )

    def test_01_merge(self):
        categ_unit = self.env.ref("uom.product_uom_categ_unit")
        uom_a = self._create_uom("TestUoM-A", categ_unit.id)
        uom_b = self._create_uom("TestUoM-B", categ_unit.id)
        uom_a_id = uom_a.id
        uom_b_id = uom_b.id
        wizard_id = self.merge_uom_wizard_model.create(
            {
                "object_ids": (uom_a + uom_b).ids,
                "dst_object_id": uom_a.id,
            }
        )
        wizard_id.action_merge()
        self.assertTrue(uom_a.exists())
        self.assertFalse(uom_b.exists())

    def test_02_merge_no_right(self):
        categ_unit = self.env.ref("uom.product_uom_categ_unit")
        uom_a = self._create_uom("TestUoM-C", categ_unit.id)
        uom_b = self._create_uom("TestUoM-D", categ_unit.id)
        wizard_id = self.merge_uom_wizard_model.with_user(self.user).create(
            {
                "object_ids": (uom_a + uom_b).ids,
                "dst_object_id": uom_a.id,
            }
        )
        with self.assertRaises(AccessDenied):
            wizard_id.action_merge()
