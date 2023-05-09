# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

from odoo.addons.tagging.tests.common import TestTaggingCommon


class TestProductTagging(TestTaggingCommon):
    """ """

    def setUp(self):
        super().setUp()
        self.product_5 = self.env.ref("product.product_product_5")
        self.product_6 = self.env.ref("product.product_product_6")
        self.product_7 = self.env.ref("product.product_product_7")
        self.product_8 = self.env.ref("product.product_product_8")
        self.product_9 = self.env.ref("product.product_product_9")

    def test_01_template_variant_paradigm(self):
        tag_ids = self.tag_1 + self.tag_2
        self.product_5.write({"tagging_ids": [(6, 0, tag_ids.ids)]})
        self.assertEqual(len(self.product_5.tagging_ids), 2)
        self.assertEqual(len(self.product_5.product_tmpl_id.tagging_ids), 2)
        self.product_5.product_tmpl_id.write({"tagging_ids": [(4, self.tag_3.id)]})
        self.assertEqual(len(self.product_5.tagging_ids), 3)
        self.assertEqual(len(self.product_5.product_tmpl_id.tagging_ids), 3)
        # check that variants and template own the same tags set
        self.assertEqual(
            set(self.product_5.product_tmpl_id.tagging_ids.ids),
            set(self.product_5.tagging_ids.ids),
        )

    def test_02_count(self):
        self.product_5.write({"tagging_ids": [(6, 0, (self.tag_1 + self.tag_2).ids)]})
        self.product_6.write({"tagging_ids": [(6, 0, (self.tag_1 + self.tag_4).ids)]})
        self.product_7.write({"tagging_ids": [(6, 0, (self.tag_3 + self.tag_4).ids)]})
        self.product_8.write({"tagging_ids": [(6, 0, (self.tag_1 + self.tag_4).ids)]})
        self.product_9.write({"tagging_ids": [(6, 0, (self.tag_2 + self.tag_4).ids)]})
        search = self.model.search_tagproduct()
        dict_search = {}
        for res in search:
            dict_search[res[0]] = res[1]
        self.assertEqual(dict_search[self.tag_1.name], 3)
        self.assertEqual(dict_search[self.tag_2.name], 2)
        self.assertEqual(dict_search[self.tag_3.name], 1)
        self.assertEqual(dict_search[self.tag_4.name], 4)
