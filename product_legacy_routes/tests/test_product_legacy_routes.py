# Copyright 2023 DEC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.tests.common import TransactionCase


class TestProductLegacyRoutes(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        warehouse = self.env.ref("stock.warehouse0")
        self.unit_uom_id = self.env.ref("uom.product_uom_unit")
        self.route_mto = warehouse.mto_pull_id.route_id
        self.route_buy = warehouse.buy_pull_id.route_id
        self.route_manufacture = warehouse.manufacture_pull_id.route_id
        self.route_mto_mts = self.env["stock.warehouse"]._find_global_route(
            xml_id="stock_mts_mto_rule.route_mto_mts",
            route_name=_("Make To Order + Make To Stock"),
        )

    def _create_product_wmethods(self, procure_method, supply_method):
        product_id = self.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
                "uom_id": self.unit_uom_id.id,
                "procure_method": procure_method,
                "supply_method": supply_method,
            }
        )
        return product_id

    def _create_product_wroutes(self, route_ids):
        product_id = self.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
                "uom_id": self.unit_uom_id.id,
                "route_ids": [(6, 0, route_ids.ids)],
            }
        )
        return product_id

    def test_01_mto_buy(self):
        product_id = self._create_product_wmethods(
            procure_method="make_to_order",
            supply_method="buy",
        )
        self.assertIn(self.route_mto, product_id.route_ids)
        self.assertIn(self.route_buy, product_id.route_ids)

    def test_02_mto_produce(self):
        product_id = self._create_product_wmethods(
            procure_method="make_to_order",
            supply_method="produce",
        )
        self.assertIn(self.route_mto, product_id.route_ids)
        self.assertIn(self.route_manufacture, product_id.route_ids)

    def test_03_mts_buy(self):
        product_id = self._create_product_wmethods(
            procure_method="make_to_stock",
            supply_method="buy",
        )
        self.assertNotIn(self.route_mto, product_id.route_ids)
        self.assertIn(self.route_buy, product_id.route_ids)

    def test_04_mts_produce(self):
        product_id = self._create_product_wmethods(
            procure_method="make_to_stock",
            supply_method="produce",
        )
        self.assertNotIn(self.route_mto, product_id.route_ids)
        self.assertIn(self.route_manufacture, product_id.route_ids)

    def test_05a_check_mto_buy(self):
        product_id = self._create_product_wroutes(
            route_ids=self.route_mto + self.route_buy,
        )
        self.assertEqual(product_id.procure_method, "make_to_order")
        self.assertEqual(product_id.supply_method, "buy")

    def test_05b_check_mto_buy(self):
        product_id = self._create_product_wroutes(
            route_ids=self.route_mto_mts + self.route_buy,
        )
        self.assertEqual(product_id.procure_method, "make_to_order")
        self.assertEqual(product_id.supply_method, "buy")

    def test_05c_check_mto_buy(self):
        product_id = self._create_product_wroutes(
            route_ids=self.route_mto + self.route_mto_mts + self.route_buy,
        )
        self.assertEqual(product_id.procure_method, "make_to_order")
        self.assertEqual(product_id.supply_method, "buy")

    def test_06a_check_mto_produce(self):
        product_id = self._create_product_wroutes(
            route_ids=self.route_mto + self.route_manufacture,
        )
        self.assertEqual(product_id.procure_method, "make_to_order")
        self.assertEqual(product_id.supply_method, "produce")

    def test_06b_check_mto_produce(self):
        product_id = self._create_product_wroutes(
            route_ids=self.route_mto_mts + self.route_manufacture,
        )
        self.assertEqual(product_id.procure_method, "make_to_order")
        self.assertEqual(product_id.supply_method, "produce")

    def test_06c_check_mto_produce(self):
        product_id = self._create_product_wroutes(
            route_ids=self.route_mto + self.route_mto_mts + self.route_manufacture,
        )
        self.assertEqual(product_id.procure_method, "make_to_order")
        self.assertEqual(product_id.supply_method, "produce")

    def test_07_check_mts_buy(self):
        product_id = self._create_product_wroutes(
            route_ids=self.route_buy,
        )
        self.assertEqual(product_id.procure_method, "make_to_stock")
        self.assertEqual(product_id.supply_method, "buy")

    def test_08_check_mts_produce(self):
        product_id = self._create_product_wroutes(
            route_ids=self.route_manufacture,
        )
        self.assertEqual(product_id.procure_method, "make_to_stock")
        self.assertEqual(product_id.supply_method, "produce")
