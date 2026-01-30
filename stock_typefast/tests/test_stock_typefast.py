# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo.tests.common import TransactionCase


class TestStockTypefast(TransactionCase):
    """Test Stock Typefast Module"""

    def test_01_picking_name(self):
        picking_type = self.env["stock.picking.type"].search([], limit=1)
        # Ensure we have locations
        src_location = picking_type.default_location_src_id or self.env[
            "stock.location"
        ].search([("usage", "=", "internal")], limit=1)
        dest_location = picking_type.default_location_dest_id or self.env[
            "stock.location"
        ].search([("usage", "=", "customer")], limit=1)

        picking = self.env["stock.picking"].create(
            {
                "name": "📦 WH/IN/01 Stock Picking",
                "picking_type_id": picking_type.id,
                "location_id": src_location.id,
                "location_dest_id": dest_location.id,
            }
        )
        self.assertEqual(picking.typefast_name, "WHIN01StockPicking")
