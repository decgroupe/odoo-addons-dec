# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023

import logging
import re
from datetime import timedelta

from odoo import SUPERUSER_ID, Command, api, fields
from odoo.exceptions import UserError
from odoo.tests import common
from odoo.tests.common import new_test_user

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
        self.internal_user = new_test_user(
            self.env,
            login="internal_user",
            groups="base.group_user",
        )

    def _create_mto_product(
        self, name_desc=False, buy=False, manufacture=False, vals=None
    ):
        routes = [self.route_mto.id]
        if buy:
            routes.append(self.route_buy.id)
        if manufacture:
            routes.append(self.route_manufacture.id)

        name = "Product EXINT"
        if name_desc:
            name += f" ({name_desc})"
        data = {
            "name": name,
            "type": "consu",
            "is_storable": True,
            "uom_id": self.unit_uom_id.id,
            "route_ids": [Command.set(routes)],
        }
        # `vals` can be used to override some of the default values
        # defined in `data` dict
        vals = vals or {}
        data.update(vals)
        return self.env["product.product"].create(data)

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
        product_nosupplier_local_id = self._create_mto_product(
            name_desc="No supplier (local)", buy=True
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
        product_with_supplier_local_id = self._create_mto_product(
            name_desc="With supplier (local)",
            buy=True,
            vals={"seller_ids": [Command.set([self.supplier_info1.id])]},
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
        product_nobom_id = self._create_mto_product(
            name_desc="No BoM (local)",
            manufacture=True,
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
        product_with_bom_id = self._create_mto_product(
            name_desc="(With Empty BoM) (local)",
            manufacture=True,
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
        product_with_bom_id = self._create_mto_product(
            name_desc="(With BoM) (local)",
            manufacture=True,
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
        ProcurementGroup = self.env["procurement.group"]
        ProcurementGroup.run_scheduler()

    def test_11_run_scheduler_new_cursor(self):
        """ """
        ProcurementGroup = self.env["procurement.group"]  # noqa: F841
        # from odoo.modules.registry import Registry
        # from unittest.mock import patch
        # with self.assertLogs('odoo.sql_db', logging.ERROR) as capture, \
        #         patch.object(Registry, '__new__', return_value=self.env.registry), \
        #         patch.object(Registry, 'cursor', return_value=self.env.cr):
        #     ProcurementGroup.run_scheduler(use_new_cursor=True)

    def test_12_run_scheduler_counter(self):
        """ """
        ProcurementGroup = self.env["procurement.group"]
        todo_count = ProcurementGroup._get_scheduler_tasks_to_do()
        scheduler_task_done = {}
        ProcurementGroup.with_context(
            scheduler_task_done=scheduler_task_done
        ).run_scheduler()
        self.assertEqual(scheduler_task_done.get("task_done", 0), todo_count)

    def test_20_exception_rule_product(self):
        """ """
        ProcurementException = self.env["procurement.exception"]
        product_noroute = self._create_mto_product(name_desc="No route (local)")
        another_product_noroute = self._create_mto_product(
            name_desc="No route (local) (another)"
        )
        _rule1 = ProcurementException.create(
            {
                "name": "Rule 1",
                "sequence": 1,
                "user_id": self.internal_user.id,
                "product_id": another_product_noroute.id,
            }
        )
        try:
            self._create_make_procurement(
                product_noroute,
                15.00,
                product_noroute.uom_id,
                self.warehouse1,
            )
        except UserError:
            _logger.info("Procurement raised an exception as expected")

        activity_id = product_noroute.activity_ids
        self.assertEqual(len(product_noroute.activity_ids), 1)
        self.assertNotEqual(activity_id.user_id, self.internal_user)
        # check that user defined in rule is not assigned the activity since regex
        # pattern does not match
        activity_id = product_noroute.activity_ids
        self.assertEqual(len(product_noroute.activity_ids), 1)
        self.assertNotEqual(activity_id.user_id, self.internal_user)
        # remove the created activity to not impact next test
        product_noroute.activity_ids.unlink()
        # retry with a valid rule
        _rule2 = ProcurementException.create(
            {
                "name": "Rule 2",
                "sequence": 2,
                "user_id": self.internal_user.id,
                "product_id": product_noroute.id,
            }
        )
        try:
            self._create_make_procurement(
                product_noroute,
                15.00,
                product_noroute.uom_id,
                self.warehouse1,
            )
        except UserError:
            _logger.info("Procurement raised an exception as expected")

        activity_id = product_noroute.activity_ids
        self.assertEqual(len(product_noroute.activity_ids), 1)
        self.assertEqual(activity_id.user_id, self.internal_user)
        self.assertEqual(activity_id.summary, "Exception")
        self.assertRegex(
            activity_id.note,
            re.compile(
                r"No rule has been found to replenish.*"
                r"Verify the routes configuration on the product.*",
                re.MULTILINE | re.IGNORECASE | re.DOTALL,
            ),
        )

    def test_21_exception_rule_category(self):
        """ """
        ProcurementException = self.env["procurement.exception"]
        main_category_id = self.env["product.category"].create(
            {"name": "Category Main"}
        )
        other_category_id = self.env["product.category"].create(
            {"name": "Category (Other)"}
        )
        product_noroute = self._create_mto_product(
            name_desc="No route (local)", vals={"categ_id": main_category_id.id}
        )
        _rule1 = ProcurementException.create(
            {
                "name": "Rule 1",
                "sequence": 1,
                "user_id": self.internal_user.id,
                "categ_id": other_category_id.id,
            }
        )
        try:
            self._create_make_procurement(
                product_noroute,
                15.00,
                product_noroute.uom_id,
                self.warehouse1,
            )
        except UserError:
            _logger.info("Procurement raised an exception as expected")

        # check that user defined in rule is not assigned the activity since regex
        # pattern does not match
        activity_id = product_noroute.activity_ids
        self.assertEqual(len(product_noroute.activity_ids), 1)
        self.assertNotEqual(activity_id.user_id, self.internal_user)
        # remove the created activity to not impact next test
        product_noroute.activity_ids.unlink()
        # retry with a valid rule
        _rule2 = ProcurementException.create(
            {
                "name": "Rule 2",
                "sequence": 2,
                "user_id": self.internal_user.id,
                "categ_id": main_category_id.id,
            }
        )
        try:
            self._create_make_procurement(
                product_noroute,
                15.00,
                product_noroute.uom_id,
                self.warehouse1,
            )
        except UserError:
            _logger.info("Procurement raised an exception as expected")

        activity_id = product_noroute.activity_ids
        self.assertEqual(len(product_noroute.activity_ids), 1)
        self.assertEqual(activity_id.user_id, self.internal_user)
        self.assertEqual(activity_id.summary, "Exception")
        self.assertRegex(
            activity_id.note,
            re.compile(
                r"No rule has been found to replenish.*"
                r"Verify the routes configuration on the product.*",
                re.MULTILINE | re.IGNORECASE | re.DOTALL,
            ),
        )

    def test_22_exception_rule_pattern(self):
        """ """
        ProcurementException = self.env["procurement.exception"]
        product_noroute = self._create_mto_product(name_desc="No route (local)")
        # create a rule with a regex pattern that does not match the exception
        # message to check
        _rule1 = ProcurementException.create(
            {
                "name": "Rule 1",
                "sequence": 1,
                "user_id": self.internal_user.id,
                "regex_pattern": "Hello world.*",
            }
        )
        try:
            self._create_make_procurement(
                product_noroute,
                15.00,
                product_noroute.uom_id,
                self.warehouse1,
            )
        except UserError:
            _logger.info("Procurement raised an exception as expected")

        # check that user defined in rule is not assigned the activity since regex
        # pattern does not match
        activity_id = product_noroute.activity_ids
        self.assertEqual(len(product_noroute.activity_ids), 1)
        self.assertNotEqual(activity_id.user_id, self.internal_user)
        # remove the created activity to not impact next test
        product_noroute.activity_ids.unlink()
        # retry with a valid rule
        _rule2 = ProcurementException.create(
            {
                "name": "Rule 2",
                "sequence": 2,
                "user_id": self.internal_user.id,
                "regex_pattern": "No rule has been found to replenish.*",
            }
        )
        try:
            self._create_make_procurement(
                product_noroute,
                15.00,
                product_noroute.uom_id,
                self.warehouse1,
            )
        except UserError:
            _logger.info("Procurement raised an exception as expected")
        # check that user defined in rule is now assigned the activity since regex
        # pattern matches the exception message
        activity_id = product_noroute.activity_ids
        self.assertEqual(len(product_noroute.activity_ids), 1)
        self.assertEqual(activity_id.user_id, self.internal_user)
        self.assertEqual(activity_id.summary, "Exception")
        self.assertRegex(
            activity_id.note,
            re.compile(
                r"No rule has been found to replenish.*"
                r"Verify the routes configuration on the product.*",
                re.MULTILINE | re.IGNORECASE | re.DOTALL,
            ),
        )
