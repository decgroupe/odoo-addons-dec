# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023

import logging
from datetime import timedelta

from odoo import SUPERUSER_ID, api, fields
from odoo.exceptions import UserError
from odoo.tests import common

_logger = logging.getLogger(__name__)


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
                "partner_id": self.vendor1.id,
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
            or (fields.datetime.now() + timedelta(days=10)),
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

    def test_01_buy_product_nosupplier_demo(self):
        """To test the creation of procurement exception activity when we try to run
        a procurement for a product without supplier, we need to commit our transaction
        to have the activity created and visible in our test transaction.
        The use of `with self.env.registry.cursor() as cr:` will commit changes each
        time we exit the `with` block.
        """
        # delete activities linked to existing product from demo data.
        # we need to do it in its own step in order to commit our changes but also
        # because it will be the database state for next step.
        with self.env.registry.cursor() as cr:
            env0 = api.Environment(cr, SUPERUSER_ID, {})
            product_nosupplier_id = env0.ref(
                "procurement_exception.product_exint_nosupplier"
            )
            self.assertTrue(product_nosupplier_id.exists())
            product_nosupplier_id.activity_ids.unlink()

        # create and run a procurement that will raises an exception about missing
        # a supplier. But we cannot check if an activity is created here because it is
        # done in another transaction. So we close this step cursor and we will do our
        # real test check in the next step.
        with self.env.registry.cursor() as cr:
            env1 = api.Environment(cr, SUPERUSER_ID, {})
            product_nosupplier_id = env1.ref(
                "procurement_exception.product_exint_nosupplier"
            )
            self.assertTrue(product_nosupplier_id.exists())
            self.assertEqual(len(product_nosupplier_id.activity_ids), 0)

            try:
                self._create_make_procurement(
                    product_nosupplier_id,
                    15.00,
                    product_nosupplier_id.uom_id,
                    self.warehouse1,
                )
            except UserError:
                _logger.info("Procurement raised an exception as expected")

            # the activity is not created in this transaction, so we check that there
            # is still no activity linked to the product.
            self.assertEqual(len(product_nosupplier_id.activity_ids), 0)

        # the database state is re-synced so we we can now test if the exception
        # activity has been created.
        with self.env.registry.cursor() as cr:
            env2 = api.Environment(cr, SUPERUSER_ID, {})
            product_nosupplier_id = env2.ref(
                "procurement_exception.product_exint_nosupplier"
            )
            self.assertTrue(product_nosupplier_id.exists())
            self.assertEqual(len(product_nosupplier_id.activity_ids), 1)
            activity_id = product_nosupplier_id.activity_ids
            self.assertRegex(
                activity_id.note,
                "There is no matching vendor price to generate "
                "the purchase order for product",
            )
            self.assertRegex(
                activity_id.note,
                "Go on the product form and complete the list of vendors.",
            )
            # delete the created activity to not impact next tests
            product_nosupplier_id.activity_ids.unlink()
            self.assertEqual(len(product_nosupplier_id.activity_ids), 0)

    def test_02_buy_product_nosupplier_local(self):
        """Since the product is created from this test context, it will not exist
        outside this transaction until a commit.
        """
        product_nosupplier_local_id = self.env["product.product"].create(
            {
                "name": "Product EXINT (No supplier) (local)",
                "type": "consu",
                "is_storable": True,
                "uom_id": self.unit_uom_id.id,
                "route_ids": [(6, 0, [self.route_buy.id, self.route_mto.id])],
            }
        )
        with self.assertRaises(UserError):
            self._create_make_procurement(
                product_nosupplier_local_id,
                15.00,
                product_nosupplier_local_id.uom_id,
                self.warehouse1,
            )
        # the procurement raises an exception but the "with ... assertRaises" context
        # will rollback the transaction so we cannot test that an activity is created
        # in this transaction
        self.assertEqual(len(product_nosupplier_local_id.activity_ids), 0)
        # retry without the assertRaises context to be able to check that an activity
        # is effectively created.
        try:
            self._create_make_procurement(
                product_nosupplier_local_id,
                15.00,
                product_nosupplier_local_id.uom_id,
                self.warehouse1,
            )
        except UserError:
            _logger.info("Procurement raised an exception as expected")
        # the activity should be created
        self.assertEqual(len(product_nosupplier_local_id.activity_ids), 1)
        activity_id = product_nosupplier_local_id.activity_ids
        self.assertRegex(
            activity_id.note,
            "There is no matching vendor price to generate "
            "the purchase order for product",
        )
        self.assertRegex(
            activity_id.note, "Go on the product form and complete the list of vendors."
        )

    def test_03_buy_product_with_supplier_local(self):
        """ """
        product_with_supplier_local_id = self.env["product.product"].create(
            {
                "name": "Product EXINT (With supplier) (local)",
                "type": "consu",
                "is_storable": True,
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

    def test_04_manufacture_product_nobom_local(self):
        """ """
        product_nobom_id = self.env["product.product"].create(
            {
                "name": "Product EXINT (No BoM) (local)",
                "type": "consu",
                "is_storable": True,
                "uom_id": self.unit_uom_id.id,
                "route_ids": [(6, 0, [self.route_manufacture.id, self.route_mto.id])],
            }
        )
        try:
            self._create_make_procurement(
                product_nobom_id,
                15.00,
                product_nobom_id.uom_id,
                self.warehouse1,
            )
        except UserError:
            _logger.info("Procurement raised an exception as expected")
        activity_id = product_nobom_id.activity_ids
        self.assertEqual(len(product_nobom_id.activity_ids), 1)
        self.assertRegex(activity_id.note, "There is no Bill of Material found")
        self.assertRegex(
            activity_id.note, "Please define a Bill of Material for this product."
        )

    def test_05_manufacture_product_with_empty_bom_local(self):
        """ """
        product_with_bom_id = self.env["product.product"].create(
            {
                "name": "Product EXINT (With BoM) (local)",
                "type": "consu",
                "is_storable": True,
                "uom_id": self.unit_uom_id.id,
                "route_ids": [(6, 0, [self.route_manufacture.id, self.route_mto.id])],
            }
        )
        _bom_id = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": product_with_bom_id.product_tmpl_id.id,
                "product_id": product_with_bom_id.id,
                "product_uom_id": self.unit_uom_id.id,
                "sequence": 1,
            }
        )
        try:
            self._create_make_procurement(
                product_with_bom_id,
                15.00,
                product_with_bom_id.uom_id,
                self.warehouse1,
            )
        except UserError:
            _logger.info("Procurement raised an exception as expected")
        activity_id = product_with_bom_id.activity_ids
        self.assertEqual(len(product_with_bom_id.activity_ids), 1)
        self.assertRegex(
            activity_id.note, "Bill of Material .* is empty for the product .*"
        )
        self.assertRegex(
            activity_id.note,
            "Please add at least one component to this Bill of Material",
        )

    def test_06_manufacture_product_with_bom_local(self):
        """ """
        product_with_bom_id = self.env["product.product"].create(
            {
                "name": "Product EXINT (With BoM) (local)",
                "type": "consu",
                "is_storable": True,
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
        _bom_line_id = self.env["mrp.bom.line"].create(
            {
                "bom_id": bom_id.id,
                "product_id": self.env.ref("product.product_product_4").id,
                "product_qty": 1,
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
        self.assertEqual(production_id.state, "confirmed")

    def test_10_run_scheduler(self):
        """ """
        self.env["procurement.group"].run_scheduler()
