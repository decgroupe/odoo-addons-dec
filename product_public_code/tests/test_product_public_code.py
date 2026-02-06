# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from odoo import Command
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestProductPublicCode(TransactionCase):
    def setUp(self):
        super().setUp()

        self.size_attribute = self.env["product.attribute"].create(
            {
                "name": "Size",
                "value_ids": [
                    Command.create({"name": "Size 1"}),
                    Command.create({"name": "Size 2"}),
                ],
            }
        )

        self.color_attribute = self.env["product.attribute"].create(
            {
                "name": "Color",
                "value_ids": [
                    Command.create({"name": "red", "sequence": 1}),
                    Command.create({"name": "green", "sequence": 2}),
                    Command.create({"name": "blue", "sequence": 3}),
                ],
            }
        )

        # create a product template with 2 variants
        self.product_tmpl = self.env["product.template"].create(
            {
                "name": "Test Product Template",
                "type": "consu",
                "is_storable": False,
                "attribute_line_ids": [
                    Command.create(
                        {  # no variants for this one
                            "attribute_id": self.size_attribute.id,
                            "value_ids": [
                                Command.link(
                                    self.size_attribute.value_ids[0].id
                                )  # Size 1
                            ],
                        }
                    ),
                    Command.create(
                        {  # two variants for this one
                            "attribute_id": self.color_attribute.id,
                            "value_ids": [
                                Command.link(
                                    self.color_attribute.value_ids[0].id
                                ),  # red
                                Command.link(
                                    self.color_attribute.value_ids[1].id
                                ),  # green
                                Command.link(
                                    self.color_attribute.value_ids[2].id
                                ),  # blue
                            ],
                        }
                    ),
                ],
            }
        )
        self.product_variant1, self.product_variant2, self.product_variant3 = (
            self.product_tmpl.product_variant_ids
        )
        self.product_variant1.write({"public_code": "P4X9255-RED"})
        self.product_variant2.write({"public_code": "P4X9324-GRE"})
        self.product_variant3.write({"public_code": False})

        # create 12 other product templates
        self.pt_ids = self.env["product.template"]
        for i in range(12):
            pt = self.env["product.template"].create(
                {
                    "name": f"Product Template #{i+1:02d}",
                    "type": "consu",
                    "public_code": f"PT-{i+1:02d}",
                }
            )
            self.pt_ids |= pt

        # create three product templates with name/code that could match the
        # public code search
        self.similar_name_pt1 = self.env["product.template"].create(
            {
                "name": "PT-00X-Product Template Similar Name 1",
                "default_code": "ABC",
                "type": "consu",
            }
        )
        self.similar_name_pt2 = self.env["product.template"].create(
            {
                "name": "Product Template Similar Name 2",
                "default_code": "PT-00Y",
                "type": "consu",
            }
        )
        self.similar_name_pt3 = self.env["product.template"].create(
            {
                "name": "Product Template Similar Name 3",
                "default_code": "PT-00Z",
                "type": "consu",
                "sale_ok": False,
            }
        )

    def _sale_default_search_domain(self):
        return [("sale_ok", "=", True)]

    def test_01_compute_public_code(self):
        # check that the public code of the template is "False" when more that one
        # variant exists
        self.assertEqual(self.product_tmpl.public_code, False)
        # create a new product template with only one variant and check that the
        # public code of the template is the same as the one of the variant
        simple_product_tmpl = self.env["product.template"].create(
            {"name": "Another Product Template", "type": "consu"}
        )
        # set a public code on the only variant of the second template and check that
        # it is updated on the template
        simple_product_variant = simple_product_tmpl.product_variant_id
        simple_product_variant.public_code = "12345-ONLY"
        self.assertEqual(simple_product_tmpl.public_code, "12345-ONLY")
        # change the public code of the first variant and check that it is updated on
        # the template
        simple_product_variant.public_code = "12345-CHANGED"
        self.assertEqual(simple_product_tmpl.public_code, "12345-CHANGED")

    def test_02_search_for_public_code(self):
        # search from template
        search_results = self.env["product.template"].search(
            [("public_code", "ilike", "P4X")]
        )
        self.assertFalse(search_results)
        # search from variant
        search_results_variant = self.env["product.product"].search(
            [("public_code", "ilike", "P4X")]
        )
        self.assertTrue(len(search_results_variant) == 2)

    def test_03_name_search_with_public_code_on_template(self):
        # search for a product template using the public code of one of its variants
        # limit to 8 (like the web UI)
        Template = self.env["product.template"].with_context(search_public_code=True)
        search_results = Template.name_search(
            "PT-", args=self._sale_default_search_domain(), limit=8
        )
        # more than 8 results are expected (in current bad implementation)
        self.assertTrue(len(search_results) > 8)
        # in facts the search should be 2 + 8 (2 matching the name/default code
        # and 8 matching the public code)
        self.assertTrue(len(search_results) >= 10)
        # same search without limit
        search_results = Template.name_search(
            "PT-", args=self._sale_default_search_domain()
        )
        search_ids = [res[0] for res in search_results]
        for pt_id in (
            self.pt_ids + self.similar_name_pt1 + self.similar_name_pt2
        ).mapped("id"):
            self.assertIn(pt_id, search_ids)
        # same search without limit and without sale_ok domain (to check that the
        # wildcard works and remove the domain)
        search_results = Template.name_search(
            "*PT-", args=self._sale_default_search_domain()
        )
        self.assertTrue(len(search_results) >= 11)
        search_ids = [res[0] for res in search_results]
        self.assertIn(self.similar_name_pt3.id, search_ids)

    def test_04_name_search_with_public_code_on_product(self):
        # search for a product template using the public code of one of its variants
        # limit to 8 (like the web UI)
        Variant = self.env["product.product"].with_context(search_public_code=True)
        search_results = Variant.name_search(
            "PT-", args=self._sale_default_search_domain(), limit=8
        )
        # more than 8 results are expected (in current bad implementation)
        self.assertTrue(len(search_results) > 8)
        # in facts the search should be 2 + 8 (2 matching the name/default code
        # and 8 matching the public code)
        self.assertTrue(len(search_results) >= 10)
        # same search without limit
        search_results = Variant.name_search(
            "PT-", args=self._sale_default_search_domain()
        )
        search_ids = [res[0] for res in search_results]
        for pv_id in (
            self.pt_ids.product_variant_ids
            + self.similar_name_pt1.product_variant_ids
            + self.similar_name_pt2.product_variant_ids
        ).mapped("id"):
            self.assertIn(pv_id, search_ids)
        # same search without limit and without sale_ok domain (to check that the
        # wildcard works and remove the domain)
        search_results = Variant.name_search(
            "*PT-", args=self._sale_default_search_domain()
        )
        self.assertTrue(len(search_results) >= 11)
        search_ids = [res[0] for res in search_results]
        self.assertIn(self.similar_name_pt3.product_variant_id.id, search_ids)

    def test_05_sale_line_form_product_onchange(self):
        partner_a = self.env["res.partner"].create({"name": "Partner A"})
        with Form(self.env["sale.order"]) as so_form:
            so_form.partner_id = partner_a
            with so_form.order_line.new() as sale_line:
                sale_line.product_id = self.similar_name_pt1.product_variant_id
            sale_order = so_form.save()
        sale_order_line = sale_order.order_line[0]
        self.assertEqual(
            sale_order_line.name, "[ABC] PT-00X-Product Template Similar Name 1"
        )
        # set a public code on this product and retry
        self.similar_name_pt1.public_code = "DEF"
        with Form(self.env["sale.order"]) as so_form:
            so_form.partner_id = partner_a
            with so_form.order_line.new() as sale_line:
                sale_line.product_id = self.similar_name_pt1.product_variant_id
            sale_order = so_form.save()
        sale_order_line = sale_order.order_line[0]
        self.assertEqual(
            sale_order_line.name, "[DEF] PT-00X-Product Template Similar Name 1"
        )
