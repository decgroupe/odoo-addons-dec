# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.exceptions import AccessDenied

from .common import TestUomMergeCommon


class TestUomMerge(TestUomMergeCommon):
    """Tests for uom_merge module."""

    def test_01_merge(self):
        """Check that two UoM records can be merged by an authorized user."""
        categ_unit = self.env.ref("uom.product_uom_categ_unit")
        uom_a = self._create_uom("TestUoM-A", categ_unit.id)
        uom_b = self._create_uom("TestUoM-B", categ_unit.id)
        wizard_id = self.merge_uom_wizard_model.create(
            {
                "object_ids": (uom_a + uom_b).ids,
                "dst_object_id": uom_a.id,
            }
        )
        wizard_id.action_merge()
        self.assertTrue(uom_a.exists())
        self.assertFalse(uom_b.exists())

    def test_02_merge_no_right(self):
        """Check that merging without the right group raises AccessDenied."""
        categ_unit = self.env.ref("uom.product_uom_categ_unit")
        uom_a = self._create_uom("TestUoM-C", categ_unit.id)
        uom_b = self._create_uom("TestUoM-D", categ_unit.id)
        wizard_id = self.merge_uom_wizard_model.with_user(self.user).create(
            {
                "object_ids": (uom_a + uom_b).ids,
                "dst_object_id": uom_a.id,
            }
        )
        with self.assertRaises(AccessDenied):
            wizard_id.action_merge()

    def test_03_skip_category_validation(self):
        """Check that _check_category_reference_uniqueness is skipped with flag."""
        categ_unit = self.env.ref("uom.product_uom_categ_unit")
        uom = self._create_uom("TestUoM-E", categ_unit.id)
        # calling with the skip flag should return early without raising
        uom.with_context(
            skip_uom_category_validation=True
        )._check_category_reference_uniqueness()
