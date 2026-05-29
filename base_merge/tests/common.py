# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo_test_helper import FakeModelLoader

from odoo.tests.common import TransactionCase


class TestBaseMergeCommon(TransactionCase):
    """Shared setup and helpers for base_merge tests."""

    def setUp(self):
        """Register fake models and expose common model handles."""
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        # the fake classes are imported after registry backup.
        # pylint: disable=import-outside-toplevel
        from .models import (
            MergeTestHolder,
            MergeTestModel,
            MergeTestTag,
            MergeTestWizard,
        )

        self.loader.update_registry(
            (MergeTestTag, MergeTestModel, MergeTestHolder, MergeTestWizard)
        )
        self.merge_model = self.env["merge.test.model"]
        self.holder_model = self.env["merge.test.holder"]
        self.tag_model = self.env["merge.test.tag"]
        self.wizard_model = self.env["merge.test.model.wizard"]

    def tearDown(self):
        """Restore original registry after each test."""
        self.loader.restore_registry()
        super().tearDown()

    def _create_xmlid(self, record, name):
        """Create one XML-ID for the provided record."""
        return self.env["ir.model.data"].create(
            {
                "module": "base_merge",
                "name": name,
                "model": record._name,
                "res_id": record.id,
            }
        )
