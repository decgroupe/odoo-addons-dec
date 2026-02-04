# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from datetime import timedelta

from freezegun import freeze_time

from odoo import Command, fields
from odoo.tests import TransactionCase


class TestSaleDeliveryLastDate(TransactionCase):
    def _create_product(self, name, sale_delay):
        product = self.env["product.product"].create(
            {
                "name": name,
                "is_storable": True,
                "sale_delay": sale_delay,
                "uom_id": 1,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            product, self.warehouse.lot_stock_id, 10
        )
        return product

    def setUp(self):
        super().setUp()
        self.warehouse = self.env.ref("stock.warehouse0")

    def test_01_dates(self):
        """Test expected date and effective date of Sales Orders"""
        product_A = self._create_product("Product A", 5)
        product_B = self._create_product("Product B", 10)
        product_C = self._create_product("Product C", 15)

        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env["res.partner"].create({"name": "A Customer"}).id,
                "picking_policy": "direct",
                "order_line": [
                    Command.create(
                        {
                            "name": product_A.name,
                            "product_id": product_A.id,
                            "customer_lead": product_A.sale_delay,
                            "product_uom_qty": 5,
                        }
                    ),
                    Command.create(
                        {
                            "name": product_B.name,
                            "product_id": product_B.id,
                            "customer_lead": product_B.sale_delay,
                            "product_uom_qty": 5,
                        }
                    ),
                    Command.create(
                        {
                            "name": product_C.name,
                            "product_id": product_C.id,
                            "customer_lead": product_C.sale_delay,
                            "product_uom_qty": 5,
                        }
                    ),
                ],
            }
        )

        # if Shipping Policy is set to `direct`(when SO is in draft state) then
        # expected date should be current date + longest lead time from all of it's
        # order lines
        expected_date = fields.Datetime.now() + timedelta(days=15)
        self.assertAlmostEqual(
            expected_date,
            sale_order.expected_last_date,
            msg="Wrong expected last date on sale order!",
            delta=timedelta(seconds=1),
        )

        # if Shipping Policy is set to `one`(when SO is in draft state) then expected
        # date should be current date + longest lead time from all of it's order lines
        sale_order.write({"picking_policy": "one"})
        self.assertAlmostEqual(
            sale_order.expected_date,
            sale_order.expected_last_date,
            msg="Wrong expected last date on sale order!",
            delta=timedelta(seconds=1),
        )

        sale_order.action_confirm()

        # Setting confirmation date of SO to 5 days from today so that the
        # expected/effective date could be checked against real confirmation date
        confirm_date = fields.Datetime.now() + timedelta(days=5)
        sale_order.write({"date_order": confirm_date})

        # if Shipping Policy is set to `one`(when SO is confirmed) then expected date
        # should be SO confirmation date + longest lead time from all of it's order
        # lines
        expected_date = confirm_date + timedelta(days=15)
        self.assertAlmostEqual(
            expected_date,
            sale_order.expected_date,
            msg="Wrong expected date on sale order!",
            delta=timedelta(seconds=1),
        )
        self.assertAlmostEqual(
            sale_order.expected_date,
            sale_order.expected_last_date,
            msg="Wrong expected last date on sale order!",
            delta=timedelta(seconds=1),
        )

        # if Shipping Policy is set to `direct`(when SO is confirmed) then expected
        # date should be SO confirmation date + shortest lead time from all of it's
        # order lines
        sale_order.write({"picking_policy": "direct"})
        expected_date = confirm_date + timedelta(days=15)
        self.assertAlmostEqual(
            expected_date,
            sale_order.expected_last_date,
            msg="Wrong expected last date on sale order!",
            delta=timedelta(seconds=1),
        )

        # Check effective date, it should be date on which the first shipment
        # successfully delivered to customer
        self.assertFalse(
            sale_order.effective_last_date,
            "Effective last date on sale order should be empty before delivery!",
        )
        picking_1 = sale_order.picking_ids
        # set product A delivered
        _2days_later = fields.Date.today() + timedelta(days=2)
        with freeze_time(_2days_later):
            picking_1.move_ids[0].picked = True
            # validate first picking (a backorder for product B and C should remain)
            picking_1._action_done()
            picking_2 = sale_order.picking_ids - picking_1
            self.assertEqual(
                _2days_later,
                sale_order.effective_last_date,
                msg="Wrong effective date on sale order!",
            )
        # set product B and C delivered
        _4days_later = fields.Date.today() + timedelta(days=4)
        with freeze_time(_4days_later):
            picking_2.move_ids[0].picked = True
            picking_2.move_ids[1].picked = True
            picking_2._action_done()
            self.assertEqual(
                _4days_later,
                sale_order.effective_last_date,
                msg="Wrong effective last date on sale order!",
            )
            self.assertEqual(
                _2days_later,
                sale_order.effective_date.date(),
                msg="Wrong effective date on sale order!",
            )
