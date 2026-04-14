# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMrpBomTrackComponentsCommon(TransactionCase):
    """Base class with shared fixtures for mrp_bom_track_components tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data: products and BoM."""
        super().setUpClass()
        cls.product_comp = cls.env["product.product"].create(
            {
                "name": "Tracked Component",
                "type": "consu",
            }
        )
        cls.product_comp2 = cls.env["product.product"].create(
            {
                "name": "Other Component",
                "type": "consu",
            }
        )
        cls.product_finished = cls.env["product.product"].create(
            {
                "name": "Finished Product",
                "type": "consu",
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_finished.product_tmpl_id.id,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_comp.id,
                            "product_qty": 1.0,
                        }
                    ),
                ],
            }
        )
