# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

import re

from odoo.tests.common import Form, SavepointCase
from odoo.exceptions import UserError


class TestPurchaseProductPack(SavepointCase):

    def _get_component_prices_sum(self, product_pack):
        component_prices = 0.0
        for pack_line in product_pack.get_pack_lines():
            product_line_price = pack_line.product_id.standard_price
            component_prices += product_line_price * pack_line.quantity
        return component_prices

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test",
                "company_id": cls.env.company.id,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                        },
                    )
                ],
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "company_id": cls.env.company.id,
                # Azure Interior
                "partner_id": cls.env.ref("base.res_partner_12").id,
                # "pricelist_id": pricelist.id,
            }
        )
        cls.PurchaseOrderLine = cls.env["purchase.order.line"]

    def setUp(self):
        super().setUp()

    def test_01_create_components_price_order_line(self):
        product_cp = self.env.ref("product_pack.product_pack_cpu_detailed_components")
        self.PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order.id,
                "name": product_cp.name,
                "product_id": product_cp.id,
                "product_qty": 1,
            }
        )
        # After create, there will be four lines
        self.assertEqual(len(self.purchase_order.order_line), 4)
        pack_line = self.purchase_order.order_line.filtered(
            lambda line: line.product_id == product_cp
        )
        # Check if sequence is the same as pack product one
        sequence = pack_line.sequence
        self.assertEqual(
            [sequence, sequence, sequence, sequence],
            self.purchase_order.order_line.mapped("sequence"),
        )
        # The products of those four lines are the main product pack and its
        # product components
        self.assertEqual(
            self.purchase_order.order_line.mapped("product_id"),
            product_cp | product_cp.get_pack_lines().mapped("product_id"),
        )

    def test_02_create_ignored_price_order_line(self):
        product_tp = self.env.ref("product_pack.product_pack_cpu_detailed_ignored")
        line = self.PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order.id,
                "name": product_tp.name,
                "product_id": product_tp.id,
                "product_qty": 1,
            }
        )
        # After create, there will be four lines
        self.assertEqual(len(self.purchase_order.order_line), 4)
        # The products of those four lines are the main product pack and its
        # product components
        self.assertEqual(
            self.purchase_order.order_line.mapped("product_id"),
            product_tp | product_tp.get_pack_lines().mapped("product_id"),
        )
        # All component lines have zero as subtotal
        self.assertEqual(
            (self.purchase_order.order_line - line).mapped("price_subtotal"), [0, 0, 0]
        )
        # Pack price is different from the sum of component prices
        self.assertAlmostEqual(line.price_subtotal, 20.5)
        self.assertNotEqual(self._get_component_prices_sum(product_tp), 20.5)

    def test_03_create_totalized_price_order_line(self):
        product_tp = self.env.ref("product_pack.product_pack_cpu_detailed_totalized")
        # forced update of the pack standard price (_update_pack_standard_price)
        product_tp.pack_type = "detailed"
        line = self.PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order.id,
                "name": product_tp.name,
                "product_id": product_tp.id,
                "product_qty": 1,
            }
        )
        # After create, there will be four lines
        self.assertEqual(len(self.purchase_order.order_line), 4)
        # The products of those four lines are the main product pack and its
        # product components
        self.assertEqual(
            self.purchase_order.order_line.mapped("product_id"),
            product_tp | product_tp.get_pack_lines().mapped("product_id"),
        )
        # All component lines have zero as subtotal
        self.assertAlmostEqual(
            (self.purchase_order.order_line - line).mapped("price_subtotal"), [0, 0, 0]
        )
        # Pack purchase price is equal to the sum of component purchase prices
        self.assertAlmostEqual(line.price_subtotal, 2596.0)
        self.assertAlmostEqual(self._get_component_prices_sum(product_tp), 2596.0)

    def test_04_create_non_detailed_price_order_line(self):
        product_ndtp = self.env.ref("product_pack.product_pack_cpu_non_detailed")
        # forced update of the pack standard price (_update_pack_standard_price)
        product_ndtp.pack_type = "non_detailed"
        line = self.PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order.id,
                "name": product_ndtp.name,
                "product_id": product_ndtp.id,
                "product_uom_qty": 1,
            }
        )
        # After create, there will be only one line, because product_type is
        # not a detailed one
        self.assertEqual(self.purchase_order.order_line, line)
        # Pack price is equal to the sum of component prices
        self.assertAlmostEqual(line.price_subtotal, 2596.0)
        self.assertAlmostEqual(self._get_component_prices_sum(product_ndtp), 2596.0)

    def test_05_update_qty(self):
        """Ensure the quantities are always updated"""

        def qty_in_order():
            return sum(self.purchase_order.order_line.mapped("product_qty"))

        product_cp = self.env.ref("product_pack.product_pack_cpu_detailed_components")
        main_line = self.PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order.id,
                "name": product_cp.name,
                "product_id": product_cp.id,
                "product_qty": 1,
            }
        )
        total_qty_init = qty_in_order()
        # change qty of main order line
        main_line.product_qty = 2 * main_line.product_qty
        total_qty_updated = qty_in_order()
        # Ensure all quantities have doubled
        self.assertAlmostEqual(total_qty_init * 2, total_qty_updated)

        # Confirm the order
        self.purchase_order.button_confirm()

        # Ensure we can still update the quantity
        main_line.product_qty = 2 * main_line.product_qty
        total_qty_confirmed = qty_in_order()
        self.assertAlmostEqual(total_qty_updated * 2, total_qty_confirmed)

    def test_06_do_not_expand(self):
        product_cp = self.env.ref("product_pack.product_pack_cpu_detailed_components")
        pack_line = self.PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order.id,
                "name": product_cp.name,
                "product_id": product_cp.id,
                "product_qty": 1,
            }
        )
        # After create, there will be four lines
        self.assertEqual(len(self.purchase_order.order_line), 4)
        pack_line_update = pack_line.with_context(update_prices=True)
        self.assertTrue(pack_line_update.do_no_expand_pack_lines)
        pack_line_update = pack_line.with_context(update_pricelist=True)
        self.assertTrue(pack_line_update.do_no_expand_pack_lines)

    def test_07_create_several_lines(self):
        # Create two sale order lines with two pack products
        # Check 8 lines are created
        # Check lines sequences and order are respected
        product_cp = self.env.ref("product_pack.product_pack_cpu_detailed_components")
        product_tp = self.env.ref("product_pack.product_pack_cpu_detailed_ignored")
        vals = [
            {
                "order_id": self.purchase_order.id,
                "name": product_cp.name,
                "product_id": product_cp.id,
                "product_qty": 1,
            },
            {
                "order_id": self.purchase_order.id,
                "name": product_tp.name,
                "product_id": product_tp.id,
                "product_qty": 1,
            },
        ]
        self.PurchaseOrderLine.create(vals)
        # After create, there will be eight lines (4 + 4)
        self.assertEqual(len(self.purchase_order.order_line), 8)
        # Check if lines are well ordered
        self.assertEqual(self.purchase_order.order_line[0].product_id, product_cp)
        sequence_cp = self.purchase_order.order_line[0].sequence
        self.assertEqual(sequence_cp, self.purchase_order.order_line[1].sequence)
        self.assertEqual(sequence_cp, self.purchase_order.order_line[2].sequence)
        self.assertEqual(sequence_cp, self.purchase_order.order_line[3].sequence)

        self.assertEqual(self.purchase_order.order_line[4].product_id, product_tp)
        sequence_tp = self.purchase_order.order_line[4].sequence
        self.assertEqual(sequence_tp, self.purchase_order.order_line[5].sequence)
        self.assertEqual(sequence_tp, self.purchase_order.order_line[6].sequence)
        self.assertEqual(sequence_tp, self.purchase_order.order_line[7].sequence)

    def test_08_try_removing_pack_line_using_orm(self):
        product_cp = self.env.ref("product_pack.product_pack_cpu_detailed_components")
        pack_line = self.PurchaseOrderLine.create(
            {
                "order_id": self.purchase_order.id,
                "name": product_cp.name,
                "product_id": product_cp.id,
                "product_qty": 1,
            }
        )
        # check that the pack line and all its components are created
        self.assertEqual(len(self.purchase_order.order_line), 4)
        # try to remove the last line
        with self.assertRaisesRegex(
            UserError,
            re.compile(
                r"You cannot delete these lines because they are part of a pack in "
                r"this purchase order:.*"
                r"To remove these lines, you need to delete the pack itself",
                re.MULTILINE | re.IGNORECASE | re.DOTALL,
            ),
        ), self.cr.savepoint():
            po = self.purchase_order.with_context(silent_UserError=True)
            po.order_line[3].unlink()
        # try to remove the first line (the pack itself)
        self.purchase_order.order_line[0].unlink()
        # check that the pack and all its components are removed
        self.assertEqual(len(self.purchase_order.order_line), 0)
        print(1)

    def test_09_try_removing_pack_line_using_form(self):
        product_cp = self.env.ref("product_pack.product_pack_cpu_detailed_components")
        with Form(self.purchase_order) as order_form:
            with order_form.order_line.new() as line:
                line.product_id = product_cp
        # check that the pack line and all its components are created
        self.assertEqual(len(self.purchase_order.order_line), 4)
        # try to remove the last line
        with self.assertRaisesRegex(
            UserError,
            re.compile(
                r"You cannot delete these lines because they are part of a pack in "
                r"this purchase order:.*"
                r"To remove these lines, you need to delete the pack itself",
                re.MULTILINE | re.IGNORECASE | re.DOTALL,
            ),
        ), self.cr.savepoint():
            with Form(
                self.purchase_order.with_context(silent_UserError=True)
            ) as order_form:
                order_form.order_line.remove(3)
        # try to remove the first line (the pack itself)
        with Form(self.purchase_order) as order_form:
            order_form.order_line.remove(0)
        # check that the pack and all its components are removed
        self.assertEqual(len(self.purchase_order.order_line), 0)
        print(1)
