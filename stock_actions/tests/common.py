# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo.addons.stock.tests.common2 import TestStockCommon
from odoo.exceptions import UserError
from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase


class TestStockActionCommon(TestStockCommon):
    """ """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MoveObj = cls.env["stock.move"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.pack_location = cls.env.ref("stock.location_pack_zone")
        cls.pack_location.active = True
        cls.route_mto = cls.warehouse_1.mto_pull_id.route_id
        cls.unit_uom_id = cls.env.ref("uom.product_uom_unit")

    def setUp(self):
        super(TestStockActionCommon, self).setUp()
        self.partner = self.env["res.partner"].create({"name": "Deco Addict"})
        self.product = self.product_3.with_user(self.user_stock_manager)
        self.product.type = "product"

    def _send_to_customer(self, product, product_uom_qty, **values):
        location_id = self.warehouse_1.lot_stock_id
        location_dest_id = self.customer_location

        picking_out = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": location_id.id,
                "location_dest_id": location_dest_id.id,
                # really important to set the right picking type, otherwise the
                # procurement will use the default company warehouse (own rules)
                "picking_type_id": self.warehouse_1.out_type_id.id,
            }
        )
        customer_move = self._create_move(
            product=product,
            src_location=location_id,
            dst_location=location_dest_id,
            product_uom_qty=product_uom_qty,
            picking_id=picking_out.id,
            # warehouse_id=self.warehouse_1.id,
            **values,
        )
        return customer_move

    def _receive_from_supplier(self, product, product_uom_qty, done=True):
        location_id = self.supplier_location
        location_dest_id = self.warehouse_1.lot_stock_id

        receive_move = self._create_move(
            product=product,
            src_location=location_id,
            dst_location=location_dest_id,
            product_uom_qty=product_uom_qty,
        )
        if done:
            receive_move.action_confirm()
            receive_move.quantity_done = product_uom_qty
            receive_move.action_done()
        return receive_move
