# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023

from datetime import timedelta

from odoo import SUPERUSER_ID, api, fields
from odoo.exceptions import UserError
from odoo.tests import common


class TestProcurementException(common.TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.warehouse1 = self.env.ref("stock.warehouse0")

        self.route_buy = self.env.ref("purchase_stock.route_warehouse0_buy")
        self.route_mto = self.warehouse1.mto_pull_id.route_id
        self.route_manufacture = self.warehouse1.manufacture_pull_id.route_id
        self.unit_uom_id = self.env.ref("uom.product_uom_unit")

        self.vendor1 = self.env["res.partner"].create(
            {"name": "AAA", "email": "from.test@example.com"}
        )
        self.vendor2 = self.env["res.partner"].create(
            {"name": "BBB", "email": "from.test2@example.com"}
        )
        self.supplier_info1 = self.env["product.supplierinfo"].create(
            {
                "name": self.vendor1.id,
                "price": 50,
            }
        )

    def _create_make_procurement(
        self, product, product_qty, uom_id, warehouse_id, date_planned=False
    ):
        ProcurementGroup = self.env["procurement.group"]
        order_values = {
            "warehouse_id": warehouse_id,
            "action": "pull_push",
            "date_planned": date_planned
            or fields.Datetime.to_string(fields.datetime.now() + timedelta(days=10)),
            # 10 days added to current date of procurement to get future schedule date
            # and order date of purchase order.
            "group_id": self.env["procurement.group"],
        }
        return ProcurementGroup.run(
            [
                self.env["procurement.group"].Procurement(
                    product,
                    product_qty,
                    uom_id,
                    warehouse_id.lot_stock_id,
                    product.name,
                    "/",
                    self.env.company,
                    order_values,
                )
            ]
        )

    def test_buy_product_nosupplier_demo_step_0(self):
        """Delete activities linked to existing product from demo data.
        We need to do it in its own step in order to commit our changes but also
        because it will be the database state for next step."""
        with self.env.registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            product_nosupplier_id = env.ref(
                "procurement_exception.product_exint_nosupplier"
            )
            self.assertTrue(product_nosupplier_id.exists())
            product_nosupplier_id.activity_ids.unlink()
            cr.commit()

    def test_buy_product_nosupplier_demo_step_1(self):
        """Create and run a procurement that will raises an exception about missing
        a supplier. But we cannot check if an activity is created here because it is
        done in another transaction. So we close this step cursor and we will do our
        real test check in the next step.
        """
        product_nosupplier_id = self.env.ref(
            "procurement_exception.product_exint_nosupplier"
        )
        self.assertTrue(product_nosupplier_id.exists())
        self.assertEqual(len(product_nosupplier_id.activity_ids), 0)
        with self.assertRaises(UserError), self.cr.savepoint():
            self._create_make_procurement(
                product_nosupplier_id,
                15.00,
                product_nosupplier_id.uom_id,
                self.warehouse1,
            )
        self.assertEqual(len(product_nosupplier_id.activity_ids), 0)

    def test_buy_product_nosupplier_demo_step_2(self):
        """The database state is re-synced so we we can now test if the exception
        activity has been created.
        """
        product_nosupplier_id = self.env.ref(
            "procurement_exception.product_exint_nosupplier"
        )
        self.assertTrue(product_nosupplier_id.exists())
        self.assertEqual(len(product_nosupplier_id.activity_ids), 1)
        activity_id = product_nosupplier_id.activity_ids
        self.assertTrue(
            "There is no matching vendor price to generate the purchase order for product"
            in activity_id.note
        )
        self.assertTrue(
            "Go on the product form and complete the list of vendors."
            in activity_id.note
        )

    def test_buy_product_nosupplier_local(self):
        """Since the product is created from this test context, it will not exist
        outside this transaction until a commit.
        """
        product_nosupplier_local_id = self.env["product.product"].create(
            {
                "name": "Product EXINT (No supplier) (local)",
                "type": "product",
                "uom_id": self.unit_uom_id.id,
                "route_ids": [(6, 0, [self.route_buy.id, self.route_mto.id])],
                # "seller_ids": [(6, 0, [supplier_info1.id])],
            }
        )
        with self.assertRaises(UserError), self.cr.savepoint():
            self._create_make_procurement(
                product_nosupplier_local_id,
                15.00,
                product_nosupplier_local_id.uom_id,
                self.warehouse1,
            )
        self.assertEqual(len(product_nosupplier_local_id.activity_ids), 1)
        activity_id = product_nosupplier_local_id.activity_ids
        self.assertTrue(
            "There is no matching vendor price to generate the purchase order for product"
            in activity_id.note
        )
        self.assertTrue(
            "Go on the product form and complete the list of vendors."
            in activity_id.note
        )

    def test_buy_product_with_supplier_local(self):
        """ """
        product_with_supplier_local_id = self.env["product.product"].create(
            {
                "name": "Product EXINT (With supplier) (local)",
                "type": "product",
                "uom_id": self.unit_uom_id.id,
                "route_ids": [(6, 0, [self.route_buy.id, self.route_mto.id])],
                "seller_ids": [(6, 0, [self.supplier_info1.id])],
            }
        )
        self._create_make_procurement(
            product_with_supplier_local_id,
            15.00,
            product_with_supplier_local_id.uom_id,
            self.warehouse1,
        )
        self.assertEqual(len(product_with_supplier_local_id.activity_ids), 0)

    def test_manufacture_product_nobom_local(self):
        """ """
        product_nobom_id = self.env["product.product"].create(
            {
                "name": "Product EXINT (No BoM) (local)",
                "type": "product",
                "uom_id": self.unit_uom_id.id,
                "route_ids": [(6, 0, [self.route_manufacture.id, self.route_mto.id])],
            }
        )
        with self.assertRaises(UserError), self.cr.savepoint():
            self._create_make_procurement(
                product_nobom_id,
                15.00,
                product_nobom_id.uom_id,
                self.warehouse1,
            )
        self.assertEqual(len(product_nobom_id.activity_ids), 1)
        activity_id = product_nobom_id.activity_ids
        self.assertTrue(
            "There is no Bill of Material of type manufacture or kit found"
            in activity_id.note
        )
        self.assertTrue(
            "Please define a Bill of Material for this product." in activity_id.note
        )

    def test_manufacture_product_with_bom_local(self):
        """ """
        product_with_bom_id = self.env["product.product"].create(
            {
                "name": "Product EXINT (With BoM) (local)",
                "type": "product",
                "uom_id": self.unit_uom_id.id,
                "route_ids": [(6, 0, [self.route_manufacture.id, self.route_mto.id])],
            }
        )
        bom_id = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": product_with_bom_id.product_tmpl_id.id,
                "product_id": product_with_bom_id.id,
                "product_uom_id": self.unit_uom_id.id,
                "sequence": 1,
            }
        )
        self._create_make_procurement(
            product_with_bom_id,
            15.00,
            product_with_bom_id.uom_id,
            self.warehouse1,
        )
        self.assertEqual(len(product_with_bom_id.activity_ids), 0)
        production_id = self.env["mrp.production"].search(
            [("product_id", "=", product_with_bom_id.id)], limit=1
        )
        self.assertTrue(production_id)
        self.assertEqual(production_id.state, "draft")

    def test_run_scheduler(self):
        """ """
        self.env["procurement.group"].run_scheduler()
        print(1)
