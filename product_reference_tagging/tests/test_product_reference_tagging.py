# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo import fields
from odoo.tests.common import TransactionCase


class TestProductReferenceTagging(TransactionCase):
    """Tests for product_reference_tagging module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.TaggingTag = cls.env["tagging.tags"]
        cls.RefProperty = cls.env["ref.property"]
        cls.RefAttribute = cls.env["ref.attribute"]
        cls.RefCategory = cls.env["ref.category"]
        cls.RefReference = cls.env["ref.reference"]
        # create a tag
        cls.tag = cls.TaggingTag.create({"name": "TestTag"})
        # create a property and attribute
        cls.property_id = cls.RefProperty.create(
            {
                "name": "Test property",
                "format": "NN",
                "fixed": True,
            }
        )
        cls.property_id.onchange_format()
        cls.attribute = cls.RefAttribute.create(
            {
                "code": "01",
                "name": "Test attribute",
                "property_id": cls.property_id.id,
            }
        )
        # create a product template and reference
        cls.category = cls.RefCategory.create(
            {"code": "TTAG", "name": "Test Tagging Category"}
        )
        cls.reference = cls.RefReference.create(
            {
                "category_id": cls.category.id,
                "name": "Test Reference Product",
                "value": "TTAG-01",
                "searchvalue": "TTAG01",
                "datetime": fields.Datetime.now(),
            }
        )

    def test_01_form_view_fields(self):
        """Check that tag form view includes reference_ids and attribute_ids."""
        view_info = self.TaggingTag.get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("reference_ids", field_names)
        self.assertIn("attribute_ids", field_names)

    def test_02_tag_on_attribute(self):
        """Check that a tag can be linked to a ref.attribute via tagging_ids."""
        self.attribute.write({"tagging_ids": [self.tag.id]})
        self.assertIn(self.tag, self.attribute.tagging_ids)
        self.assertIn(self.attribute, self.tag.attribute_ids)

    def test_03_tag_on_reference(self):
        """Check that a tag can be linked to a ref.reference via tagging_ids."""
        self.reference.write({"tagging_ids": [self.tag.id]})
        self.assertIn(self.tag, self.reference.tagging_ids)
        self.assertIn(self.reference, self.tag.reference_ids)
