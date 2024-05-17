# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.addons.stock_actions_tests.tests.common import TestStockActionTestsCommon
from odoo.tests import Form


class TestPurchaseMrpCancelTests(TestStockActionTestsCommon):
    """ """

    def _add_mto_route(self, product):
        product.route_ids += self.route_mto

    def _generate_mo(self, product, bom, qty=1.0):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        return mo

    def _get_po(self, production):
        move_ids = production.procurement_group_id.stock_move_ids
        purchase_order_ids = (
            move_ids.created_purchase_line_id.order_id
            | move_ids.move_orig_ids.purchase_line_id.order_id
        )
        return purchase_order_ids

    def _get_mo_line(self, production, product):
        res = production.move_raw_ids.filtered(lambda m: m.product_id == product)
        self.assertTrue(res)
        self.assertEqual(len(res), 1)
        return res

    def _get_po_line(self, purchase_orders, product):
        res = purchase_orders.order_line.filtered(lambda m: m.product_id == product)
        self.assertTrue(res)
        self.assertEqual(len(res), 1)
        return res

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
        self.purchase_model = self.env["purchase.order"]
        self.purchase_line_model = self.env["purchase.order.line"]
        self.production_model = self.env["mrp.production"]
        self.bom_model = self.env["mrp.bom"]

        # BoM of [FURN_7800] Desk Combination (product.product_product_3)
        # -- [FURN_0269] Office Chair Black
        # -- [FURN_1118] Corner Desk Left Sit
        # -- [FURN_8900] Drawer Black

        # [FURN_0269] Office Chair Black
        self.product12 = self.env.ref("product.product_product_12")
        self._add_mto_route(self.product12)
        # [FURN_1118] Corner Desk Left Sit
        self.product13 = self.env.ref("product.product_product_13")
        self._add_mto_route(self.product13)
        # [FURN_8900] Drawer Black
        self.product16 = self.env.ref("product.product_product_16")
        self._add_mto_route(self.product16)

    def test_01_cancel(self):
        # force quantities to zero
        self._set_stock_qty(self.product13, -self.product13.qty_available)
        self._set_stock_qty(self.product16, -self.product16.qty_available)
        product_id = self.env.ref("product.product_product_3")
        bom_id = self.bom_model.search(
            [("product_tmpl_id", "=", product_id.product_tmpl_id.id)]
        )
        self.assertTrue(bom_id)
        production_id = self._generate_mo(product_id, bom_id)
        production_id.action_confirm()
        self.assertEqual(production_id.purchase_order_count, 2)
        # test cancel without propagation
        mo_line_p13 = self._get_mo_line(production_id, self.product13)
        self.assertEqual(mo_line_p13.procure_method, "make_to_order")
        self.assertEqual(mo_line_p13.state, "waiting")
        po_ids = self._get_po(production_id)
        po_line_p13 = self._get_po_line(po_ids, self.product13)
        po_line_p13.with_context(propagate=False).action_propagate_cancel()
        self.assertEqual(mo_line_p13.procure_method, "make_to_stock")
        self.assertEqual(mo_line_p13.state, "confirmed")
        # test cancel with propagation
        mo_line_p16 = self._get_mo_line(production_id, self.product16)
        self.assertEqual(mo_line_p16.procure_method, "make_to_order")
        self.assertEqual(mo_line_p16.state, "waiting")
        po_ids = self._get_po(production_id)
        po_line_p16 = self._get_po_line(po_ids, self.product16)
        po_line_p16.with_context(propagate=True).action_propagate_cancel()
        self.assertEqual(mo_line_p16.procure_method, "make_to_stock")
        self.assertEqual(mo_line_p16.state, "cancel")
