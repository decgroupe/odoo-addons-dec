# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

from odoo.tests.common import TransactionCase


class TestUomSmartSearch(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.uom_model = self.env["uom.uom"]
        self.uom_cat_unit = self.env.ref("uom.product_uom_categ_unit")
        self.uom_cat_volume = self.env.ref("uom.product_uom_categ_vol")

    def test_01_name_search_unit_unitcat(self):
        uom_ids = self.uom_model.name_search(
            "PCE", [("category_id", "=", self.uom_cat_unit.id)]
        )
        uom_res = [x[1] for x in uom_ids]
        self.assertIn("PCE", uom_res)
        self.assertIn("2PCE", uom_res)
        self.assertIn("4PCE", uom_res)
        self.assertIn("5PCE", uom_res)
        self.assertIn("10PCE", uom_res)
        self.assertIn("20PCE", uom_res)
        self.assertIn("100PCE", uom_res)
        self.assertIn("200PCE", uom_res)
        self.assertIn("1000PCE", uom_res)
        self.assertIn("2000PCE", uom_res)
        self.assertLess(uom_res.index("PCE"), uom_res.index("2PCE"))
        self.assertLess(uom_res.index("2PCE"), uom_res.index("4PCE"))
        self.assertLess(uom_res.index("4PCE"), uom_res.index("5PCE"))
        self.assertLess(uom_res.index("5PCE"), uom_res.index("10PCE"))
        self.assertLess(uom_res.index("10PCE"), uom_res.index("20PCE"))
        self.assertLess(uom_res.index("20PCE"), uom_res.index("100PCE"))
        self.assertLess(uom_res.index("100PCE"), uom_res.index("200PCE"))
        self.assertLess(uom_res.index("200PCE"), uom_res.index("1000PCE"))
        self.assertLess(uom_res.index("1000PCE"), uom_res.index("2000PCE"))

    def test_02_name_search_value_unitcat(self):
        uom_ids = self.uom_model.name_search(
            "10", [("category_id", "=", self.uom_cat_unit.id)]
        )
        uom_res = [x[1] for x in uom_ids]
        self.assertIn("10PCE", uom_res)
        self.assertIn("100PCE", uom_res)
        self.assertIn("1000PCE", uom_res)
        self.assertLess(uom_res.index("10PCE"), uom_res.index("100PCE"))
        self.assertLess(uom_res.index("100PCE"), uom_res.index("1000PCE"))

    def test_03_name_search_value_all_categories(self):
        uom_ids = self.uom_model.name_search("10")
        uom_res = [x[1] for x in uom_ids]
        self.assertIn("10PCE", uom_res)
        self.assertIn("100PCE", uom_res)
        self.assertIn("1000PCE", uom_res)
        self.assertIn("10L", uom_res)
        self.assertIn("100L", uom_res)
        self.assertIn("1000L", uom_res)
        self.assertLess(uom_res.index("10L"), uom_res.index("10PCE"))
        self.assertLess(uom_res.index("100L"), uom_res.index("100PCE"))
        self.assertLess(uom_res.index("1000L"), uom_res.index("1000PCE"))
