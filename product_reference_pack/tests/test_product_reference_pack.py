# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from .common import TestProductReferencePackCommon


class TestProductReferencePack(TestProductReferencePackCommon):
    """Tests for product_reference_pack module."""

    def test_01_create_with_product_id_sets_defaults(self):
        """Creating a ref.pack via product_id sets pack defaults on the template."""
        ref = self.RefPack.create(
            {
                "product_id": self.product_both.id,
                "type": "company",
            }
        )
        self.assertTrue(ref.product_id.pack_ok)
        self.assertEqual(ref.product_id.pack_type, "detailed")
        self.assertEqual(ref.product_id.pack_component_price, "ignored")
        self.assertFalse(ref.product_id.pack_modifiable)

    def test_02_pack_order_type_both(self):
        """pack_order_type is 'all' when the product is sale_ok and purchase_ok."""
        ref = self.RefPack.create(
            {
                "product_id": self.product_both.id,
                "type": "company",
            }
        )
        self.assertEqual(ref.product_id.pack_order_type, "all")

    def test_03_pack_order_type_sale_only(self):
        """pack_order_type is 'sale' when the product is only sale_ok."""
        ref = self.RefPack.create(
            {
                "product_id": self.product_sale.id,
                "type": "company",
            }
        )
        self.assertEqual(ref.product_id.pack_order_type, "sale")

    def test_04_pack_order_type_purchase_only(self):
        """pack_order_type is 'purchase' when the product is only purchase_ok."""
        ref = self.RefPack.create(
            {
                "product_id": self.product_purchase.id,
                "type": "manufacturer",
            }
        )
        self.assertEqual(ref.product_id.pack_order_type, "purchase")

    def test_05_create_with_product_variant_id_resolves_template(self):
        """Creating a ref.pack via product_variant_id resolves to the product
        template."""
        variant = self.product_both.product_variant_id
        ref = self.RefPack.create(
            {
                "product_variant_id": variant.id,
                "type": "company",
            }
        )
        self.assertEqual(ref.product_id, self.product_both)

    def test_06_compute_product_variant_id(self):
        """product_variant_id is computed from the product template."""
        ref = self.RefPack.create(
            {
                "product_id": self.product_both.id,
                "type": "company",
            }
        )
        self.assertEqual(ref.product_variant_id, self.product_both.product_variant_id)

    def test_07_inverse_product_variant_id(self):
        """Writing to product_variant_id updates the product_id template."""
        ref = self.RefPack.create(
            {
                "product_id": self.product_both.id,
                "type": "company",
            }
        )
        # change variant to point to another product template
        ref.product_variant_id = self.product_sale.product_variant_id
        self.assertEqual(ref.product_id, self.product_sale)

    def test_08_list_view_fields(self):
        """Check that expected fields are present in the combined list view arch."""
        view_info = self.env["ref.pack"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("name", field_names)
        self.assertIn("product_id", field_names)
        self.assertIn("default_code", field_names)
        self.assertIn("public_code", field_names)

    def test_09_form_view_fields(self):
        """Check that expected fields are present in the combined form view arch."""
        view_info = self.env["ref.pack"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("type", field_names)
        self.assertIn("product_id", field_names)
        self.assertIn("default_code", field_names)
        self.assertIn("public_code", field_names)
        self.assertIn("list_price", field_names)
        self.assertIn("standard_price", field_names)
