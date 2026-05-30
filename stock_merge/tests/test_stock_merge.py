# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from unittest.mock import Mock, patch

from lxml import etree

from odoo.tests.common import tagged

from .common import TestStockMergeCommon


@tagged("post_install", "-at_install")
class TestStockMerge(TestStockMergeCommon):
    """Tests for stock_merge module."""

    def test_01_merge_passes_context_and_unique_xmlid(self):
        """Verify _merge forwards context and unique_xmlid to base_merge."""
        wizard = self._create_wizard()
        dst_object = Mock()
        dst_object_with_ctx = Mock()
        dst_object.with_context.return_value = dst_object_with_ctx
        with patch(
            "odoo.addons.base_merge.wizard.merge_object.MergeObject._merge",
            autospec=True,
            return_value="ok",
        ) as merge_mock:
            result = wizard._merge([10, 11], dst_object=dst_object, unique_xmlid=True)
        dst_object.with_context.assert_called_once_with(
            mail_auto_subscribe_no_notify=True
        )
        merge_mock.assert_called_once_with(wizard, [10, 11], dst_object_with_ctx, True)
        self.assertEqual(result, "ok")

    def test_02_log_merge_operation_cancels_source_moves(self):
        """Verify _log_merge_operation sets source stock moves to cancel."""
        wizard = self._create_wizard()
        src_objects = Mock()
        src_objects.ids = [1, 2]
        dst_object = Mock()
        with patch(
            "odoo.addons.base_merge.wizard.merge_object.MergeObject._log_merge_operation",
            autospec=True,
        ) as log_mock:
            wizard._log_merge_operation(src_objects, dst_object)
        log_mock.assert_called_once_with(wizard, src_objects, dst_object)
        src_objects.write.assert_called_once_with({"state": "cancel"})

    def test_03_form_view_fields(self):
        """Check expected fields are present in the merged form view arch."""
        view_info = self.merge_stock_move_wizard_model.get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("state", field_names)
        self.assertIn("dst_object_id", field_names)
        self.assertIn("object_ids", field_names)
