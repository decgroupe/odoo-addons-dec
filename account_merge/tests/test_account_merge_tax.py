# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAccountMergeTax(TransactionCase):
    def setUp(self):
        super().setUp()
        self.tax_model = self.env["account.tax"]
        self.merge_account_tax_wizard_model = self.env["merge.account.tax.wizard"]
        self.group_do_merge = self.env.ref("account_merge.res_group_do_merge")

    def test_01_merge(self):
        # get a first tax reference
        t1 = self.env.ref("l10n_generic_coa.1_sale_tax_template")
        # keep current data for future comparison
        t1_data = t1.read()[0]
        # get another tax reference that will be merged in to the first one
        t2 = self.env.ref("l10n_generic_coa.1_purchase_tax_template")
        # edit some values
        t2.write({})
        # keep current data for future comparison
        t2_data = t2.read()[0]
        # execute merge
        wizard_id = self.merge_account_tax_wizard_model.create(
            {
                "object_ids": (t1 + t2).ids,
                "dst_object_id": t1.id,
            }
        )
        wizard_id.action_merge()
        self.assertTrue(t1.exists())
        self.assertFalse(t2.exists())
        t1_new_data = t1.read()[0]
        xml_ids = self.env["ir.model.data"].search(
            [
                ("model", "=", self.tax_model._name),
                ("res_id", "=", t1_new_data["id"]),
            ]
        )
        self.assertEqual(len(xml_ids), 1)
