# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.tests.common import TransactionCase


class TestSaleMrpProductionRequestLink(TransactionCase):

    def _set_stock_qty(self, product, qty):
        self.env["stock.quant"]._update_available_quantity(
            product, self.stock_location, qty
        )

    def _get_stock_qty(self, product):
        return self.env["stock.quant"]._get_available_quantity(
            product, self.stock_location
        )

    def setUp(self):
        super().setUp()
        warehouse = self.env.ref("stock.warehouse0")
        self.unit_uom_id = self.env.ref("uom.product_uom_unit")
        self.stock_location = warehouse.lot_stock_id
        self.route_mto = warehouse.mto_pull_id.route_id
        # self.route_buy = warehouse.buy_pull_id.route_id
        self.route_manufacture = warehouse.manufacture_pull_id.route_id
        # enable MTO route
        self.route_mto.active = True
        # [FURN_7800] Desk Combination
        self.product = self.env.ref("product.product_product_3")
        self.product.mrp_production_request = True
        self.product.route_ids = [
            (4, self.route_mto.id, 0),
            (4, self.route_manufacture.id, 0),
        ]
        # create sale order with this product
        self.order_id = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_10").id,
                "user_id": self.env.ref("base.user_admin").id,
                "date_order": (datetime.now() - relativedelta(days=65)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )
        self.order_line1_id = self.env["sale.order.line"].create(
            {
                "order_id": self.order_id.id,
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
            }
        )

    def test_01_cancel_sale_order_with_draft_request(self):
        # force quantities to zero
        self._set_stock_qty(self.product, -self.product.qty_available)
        # confirm sale order
        self.assertEqual(self.order_id.production_request_count, 0)
        self.order_id.action_confirm()
        self.assertEqual(self.order_id.production_request_count, 1)
        request_id = self.order_id.production_request_ids
        self.assertEqual(request_id.sale_order_id, self.order_id)
        # store current values
        previous_activity_ids = request_id.activity_ids
        previous_message_ids = request_id.message_ids
        # cancel sale order
        self.order_id.action_cancel()
        new_message_ids = request_id.message_ids - previous_message_ids
        self.assertEqual(len(new_message_ids), 1)
        self.assertIn(
            "Automatic cancellation following cancellation of the sell order",
            new_message_ids.body,
        )
        new_activity_ids = request_id.activity_ids - previous_activity_ids
        self.assertEqual(len(new_activity_ids), 0)

    def test_02_cancel_sale_order_with_approved_request(self):
        # force quantities to zero
        self._set_stock_qty(self.product, -self.product.qty_available)
        # confirm sale order
        self.assertEqual(self.order_id.production_request_count, 0)
        self.order_id.action_confirm()
        self.assertEqual(self.order_id.production_request_count, 1)
        request_id = self.order_id.production_request_ids
        self.assertEqual(request_id.sale_order_id, self.order_id)
        # store current values
        previous_activity_ids = request_id.activity_ids
        previous_message_ids = request_id.message_ids
        # approve request
        request_id.button_to_approve()
        request_id.button_approved()
        self.assertEqual(request_id.state, "approved")
        # cancel sale order
        self.order_id.action_cancel()
        new_message_ids = request_id.message_ids - previous_message_ids
        self.assertEqual(len(new_message_ids), 0)
        new_activity_ids = request_id.activity_ids - previous_activity_ids
        self.assertEqual(len(new_activity_ids), 1)
        self.assertIn(
            "Exception(s) occurred on the sale order(s)",
            new_activity_ids.note,
        )
        self.assertIn(self.order_id.display_name, new_activity_ids.note)
        self.assertIn("Manual actions may be needed.", new_activity_ids.note)
