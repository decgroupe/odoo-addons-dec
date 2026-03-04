# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestProductReferenceCommon(TransactionCase):
    """Test the product reference module."""

    def assertNameSearch(self, record, name, expected_result):
        Model = self.env[record._name]
        Model.invalidate_model(["display_name"])
        res = Model.name_search(name=name)
        if not expected_result:
            self.assertFalse(res)
            return
        try:
            self.assertEqual(res[0][0], record.id)
            self.assertEqual(res[0][1], expected_result)
        except IndexError:
            self.fail(
                f"Expected to find a record with name_search '{name}' "
                f"but found {res}.\n"
                f"Value is '{record.display_name}'"
            )

    def setUp(self):
        super().setUp()
        self.RefCategory = self.env["ref.category"]
        self.RefProperty = self.env["ref.property"]
        self.RefAttribute = self.env["ref.attribute"]
        self.RefReference = self.env["ref.reference"]
        self.ProductTemplate = self.env["product.template"]
