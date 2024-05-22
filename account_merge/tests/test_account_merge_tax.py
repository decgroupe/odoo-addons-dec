# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAccountMergeTax(TransactionCase):

    def _create_tax(self, name, type_tax_use, amount):
        return self.env["account.tax"].create(
            {
                "name": "Test Sale Tax",
                "type_tax_use": "sale",
                "amount": "20",
            }
        )

    def __create_xmlid(self, res_model, res_id, name, module):
        return self.env["ir.model.data"].create(
            {
                "module": module,
                "name": name,
                "model": res_model,
                "res_id": res_id,
            }
        )

    def _create_xmlid(self, record_id, name, module):
        return self.__create_xmlid(record_id._name, record_id.id, name, module)

    def setUp(self):
        super().setUp()
        self.tax_model = self.env["account.tax"]
        self.merge_account_tax_wizard_model = self.env["merge.account.tax.wizard"]
        self.group_do_merge = self.env.ref("account_merge.res_group_do_merge")
        # we cannot rely on `l10n_generic_coa`, so we create our own data
        self.sale_tax = self._create_tax("Test Sale Tax", "sale", 20)
        self._create_xmlid(self.sale_tax, "test_sale_tax", "account_merge")
        self.purchase_tax = self._create_tax("Test Purchase Tax", "purchase", 20)
        self._create_xmlid(self.purchase_tax, "test_purchase_tax", "account_merge")

    def test_01_merge(self):
        # get a first tax reference
        t1 = self.sale_tax
        # keep current data for future comparison
        t1_data = t1.read()[0]
        # get another tax reference that will be merged in to the first one
        t2 = self.purchase_tax
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
