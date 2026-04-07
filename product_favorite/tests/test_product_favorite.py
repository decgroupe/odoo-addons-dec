# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from .common import TestProductFavoriteCommon


class TestProductFavorite(TestProductFavoriteCommon):
    """Tests for product_favorite module."""

    def test_01_favorite_ok_set_via_sale_order(self):
        """Verify favorite_ok is set when a product is used in a sale order."""
        self._create_sale_order(self.component_product)
        self.env["product.template"].autoset_ok()
        self.component_product.product_tmpl_id.invalidate_recordset(["favorite_ok"])
        self.assertTrue(self.component_product.product_tmpl_id.favorite_ok)
        self.unused_product.product_tmpl_id.invalidate_recordset(["favorite_ok"])
        self.assertFalse(self.unused_product.product_tmpl_id.favorite_ok)

    def test_02_favorite_ok_set_via_purchase_order(self):
        """Verify favorite_ok is set when a product is used in a purchase order."""
        self._create_purchase_order(self.component_product)
        self.env["product.template"].autoset_ok()
        self.component_product.product_tmpl_id.invalidate_recordset(["favorite_ok"])
        self.assertTrue(self.component_product.product_tmpl_id.favorite_ok)
        self.unused_product.product_tmpl_id.invalidate_recordset(["favorite_ok"])
        self.assertFalse(self.unused_product.product_tmpl_id.favorite_ok)

    def test_03_favorite_ok_set_via_bom(self):
        """Verify favorite_ok is set when a product is used as a BoM component."""
        self._create_bom(self.finished_product, self.component_product)
        self.env["product.template"].autoset_ok()
        self.component_product.product_tmpl_id.invalidate_recordset(["favorite_ok"])
        self.assertTrue(self.component_product.product_tmpl_id.favorite_ok)
        # finished product is not a component so it must not be flagged
        self.finished_product.product_tmpl_id.invalidate_recordset(["favorite_ok"])
        self.assertFalse(self.finished_product.product_tmpl_id.favorite_ok)
        self.unused_product.product_tmpl_id.invalidate_recordset(["favorite_ok"])
        self.assertFalse(self.unused_product.product_tmpl_id.favorite_ok)

    def test_04_template_display_name(self):
        """Verify emoji only appears in template display_name under name_search
        context."""
        name = self.component_product.product_tmpl_id.name
        self.component_product.product_tmpl_id.write({"favorite_ok": True})
        self.assertDisplayName(
            self.component_product.product_tmpl_id,
            name,
            f"{name} 📌",
        )
        self.component_product.product_tmpl_id.write({"favorite_ok": False})
        self.assertDisplayName(
            self.unused_product.product_tmpl_id,
            self.unused_product.product_tmpl_id.name,
            self.unused_product.product_tmpl_id.name,
        )

    def test_05_variant_display_name(self):
        """Verify emoji only appears in variant display_name under name_search
        context."""
        name = self.component_product.name
        self.component_product.product_tmpl_id.write({"favorite_ok": True})
        self.assertDisplayName(
            self.component_product,
            name,
            f"{name} 📌",
        )
        self.component_product.product_tmpl_id.write({"favorite_ok": False})
        self.assertDisplayName(
            self.unused_product,
            self.unused_product.name,
            self.unused_product.name,
        )

    def test_06_template_name_search(self):
        """Verify name_search appends emoji for favorite templates."""
        name = self.component_product.product_tmpl_id.name
        self.component_product.product_tmpl_id.write({"favorite_ok": True})
        self.assertNameSearch(
            self.component_product.product_tmpl_id,
            name,
            f"{name} 📌",
        )
        self.assertNameSearch(
            self.unused_product.product_tmpl_id,
            self.unused_product.product_tmpl_id.name,
            self.unused_product.product_tmpl_id.name,
        )

    def test_07_variant_name_search(self):
        """Verify name_search appends emoji for favorite product variants."""
        name = self.component_product.name
        self.component_product.product_tmpl_id.write({"favorite_ok": True})
        self.assertNameSearch(
            self.component_product,
            name,
            f"{name} 📌",
        )
        self.assertNameSearch(
            self.unused_product,
            self.unused_product.name,
            self.unused_product.name,
        )

    def test_08_name_search_cleans_symbol_from_input(self):
        """Verify name_search strips the 📌 symbol from the query before searching."""
        self.component_product.product_tmpl_id.write({"favorite_ok": True})
        name = self.component_product.name
        name_with_symbol = f"{name} 📌"
        # searching with the symbol still finds the product on both models
        self.assertNameSearch(
            self.component_product.product_tmpl_id,
            name_with_symbol,
            f"{name} 📌",
        )
        self.assertNameSearch(
            self.component_product,
            name_with_symbol,
            f"{name} 📌",
        )

    def test_09_form_view_fields(self):
        """Check that favorite_ok field is present in the combined product form view."""
        view_info = self.env["product.template"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("favorite_ok", field_names)
