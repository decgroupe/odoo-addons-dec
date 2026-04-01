# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo import Command
from odoo.tests.common import TransactionCase


class TestWebsiteSaleMainCategory(TransactionCase):
    """Tests for website_sale_main_category module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.categ1 = cls.env["product.public.category"].create({"name": "Category 1"})
        cls.categ2 = cls.env["product.public.category"].create({"name": "Category 2"})
        cls.categ3 = cls.env["product.public.category"].create({"name": "Category 3"})
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )

    def test_01_compute_public_categ_id_empty(self):
        """public_categ_id is False when no public_categ_ids are set."""
        self.assertFalse(self.product.public_categ_id)

    def test_02_compute_public_categ_id_single(self):
        """public_categ_id equals the single category when only one is set."""
        self.product.public_categ_ids = [Command.set([self.categ1.id])]
        self.assertEqual(self.product.public_categ_id, self.categ1)

    def test_03_compute_public_categ_id_multiple(self):
        """public_categ_id is the first category when multiple are set."""
        self.product.public_categ_ids = [
            Command.set([self.categ1.id, self.categ2.id, self.categ3.id])
        ]
        self.assertEqual(self.product.public_categ_id, self.categ1)
        # set another order and check that it also change the main category
        self.product.public_categ_ids = [
            Command.set([self.categ3.id, self.categ2.id, self.categ1.id])
        ]
        self.assertEqual(self.product.public_categ_id, self.categ3)

    def test_04_set_main_public_category_no_existing(self):
        """set_main_public_category sets the category when none exists."""
        product = self.env["product.template"].create(
            {
                "name": "Test Product 2",
                "type": "consu",
            }
        )
        product.set_main_public_category(self.categ1.id)
        self.assertEqual(product.public_categ_id, self.categ1)
        self.assertEqual(product.public_categ_ids, self.categ1)

    def test_05_set_main_public_category_replaces_first(self):
        """set_main_public_category replaces the main category, keeping others."""
        product = self.env["product.template"].create(
            {
                "name": "Test Product 3",
                "type": "consu",
                "public_categ_ids": [Command.set([self.categ1.id, self.categ2.id])],
            }
        )
        product.set_main_public_category(self.categ3.id)
        self.assertEqual(product.public_categ_id, self.categ3)
        self.assertIn(self.categ2, product.public_categ_ids)
        self.assertNotIn(self.categ1, product.public_categ_ids)

    def test_06_set_main_public_category_already_main(self):
        """set_main_public_category keeps other categories when target is
        already the first one."""
        product = self.env["product.template"].create(
            {
                "name": "Test Product 4",
                "type": "consu",
                "public_categ_ids": [Command.set([self.categ1.id, self.categ2.id])],
            }
        )
        product.set_main_public_category(self.categ1.id)
        self.assertEqual(product.public_categ_id, self.categ1)
        self.assertIn(self.categ2, product.public_categ_ids)

    def test_07_set_main_public_category_via_product_product(self):
        """set_main_public_category on product.product delegates to template."""
        product = self.env["product.template"].create(
            {
                "name": "Test Product 5",
                "type": "consu",
            }
        )
        product_product = product.product_variant_ids[0]
        product_product.set_main_public_category(self.categ2.id)
        self.assertEqual(product.public_categ_id, self.categ2)

    def test_08_search_view_fields(self):
        """Check that public_categ_id is present in the combined search view arch."""
        view_info = self.env["product.template"].get_view(view_type="search")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("public_categ_id", field_names)
