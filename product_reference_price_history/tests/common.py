# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from contextlib import contextmanager
from unittest.mock import patch

from odoo import Command
from odoo.tests.common import TransactionCase

from odoo.addons.base.models.ir_mail_server import IrMailServer


class TestProductReferencePriceHistoryCommon(TransactionCase):
    """Common fixtures for product_reference_price_history tests."""

    def setUp(self):
        """Set up shared test data: category, product with BOM, and reference."""
        super().setUp()
        self.RefCategory = self.env["ref.category"]
        self.RefReference = self.env["ref.reference"]
        self.RefPrice = self.env["ref.price"]
        # create a ref category (non-ADT so scheduler does not skip it)
        self.category = self.RefCategory.create(
            {"code": "TST", "name": "Test Category"}
        )
        # create the ADT category for skip-coverage tests
        self.adt_category = self.RefCategory.create(
            {"code": "ADT", "name": "ADT Category"}
        )
        # create a component product with a known standard price
        self.component = self.env["product.product"].create(
            {"name": "Test Component", "standard_price": 50.0}
        )
        # create the main product (template + variant)
        self.main_product = self.env["product.product"].create(
            {"name": "Test Product", "standard_price": 0.0}
        )
        self.main_tmpl = self.main_product.product_tmpl_id
        # create a BOM with one component so cost_price = 50.0
        self.bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.main_tmpl.id,
                "product_id": self.main_product.id,
                "bom_line_ids": [
                    Command.create({"product_id": self.component.id, "product_qty": 1})
                ],
            }
        )
        # create a reference pointing to the main product's variant
        # (product_variant_id must be used to avoid auto-creating a new product)
        self.reference = self.RefReference.create(
            {
                "category_id": self.category.id,
                "product_variant_id": self.main_product.id,
                "value": "TST-001",
                "searchvalue": "TST001",
            }
        )

    @contextmanager
    def mock_smtp_send(self):
        """Mock IrMailServer.send_email to prevent actual SMTP sending in tests."""

        def _fake_send(
            self_server, message, mail_server_id=None, smtp_server=None, **kwargs
        ):
            return message.get("Message-Id", "mocked")

        with patch.object(IrMailServer, "send_email", _fake_send):
            yield
