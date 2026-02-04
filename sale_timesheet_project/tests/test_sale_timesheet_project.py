# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2024

from odoo.tests import tagged

from odoo.addons.sale_timesheet.tests.common import TestCommonSaleTimesheet


@tagged("-at_install", "post_install")
class TestSaleTimesheetProject(TestCommonSaleTimesheet):
    def _create_so(self, partner_id):
        return (
            self.env["sale.order"]
            .with_context(
                mail_notrack=True,
                mail_create_nolog=True,
            )
            .create(
                {
                    "partner_id": partner_id.id,
                    "partner_invoice_id": partner_id.id,
                    "partner_shipping_id": partner_id.id,
                }
            )
        )

    def _create_so_line(self, sale_order_id):
        return self.env["sale.order.line"].create(
            {
                "order_id": sale_order_id.id,
                "name": self.product_training_service.name,
                "product_id": self.product_training_service.id,
                "product_uom_qty": 2,
                "product_uom": self.product_training_service.uom_id.id,
                "price_unit": self.product_training_service.list_price,
            }
        )

    def assertContract(self, sale_order_id, project_id):
        contract_type_id = self.env.ref("project_identification.contract_type")
        self.assertEqual(project_id.type_id, contract_type_id)
        self.assertEqual(project_id.partner_id, sale_order_id.partner_id)
        self.assertEqual(project_id.user_id, sale_order_id.user_id)
        self.assertEqual(project_id.allow_timesheets, True)
        self.assertEqual(project_id.allow_billable, True)
        # `pricing_type` cannot be `fixed_rate` since Odoo 18.0 because it implies that
        # a sale order line is linked to the project itsef
        self.assertEqual(project_id.pricing_type, "task_rate")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.project_model = cls.env["project.project"]

        # Create service products
        uom_day = cls.env.ref("uom.product_uom_day")
        cls.product_training_service = cls.env["product.product"].create(
            {
                "name": "On-site Training",  # Formation sur site
                "standard_price": 768,
                "list_price": 948,
                "type": "service",
                "service_policy": "ordered_timesheet",
                "uom_id": uom_day.id,
                "uom_po_id": uom_day.id,
                "default_code": "BRD_OST",
                "service_tracking": "task_in_project",
                "project_id": False,
                "taxes_id": False,
            }
        )

    def setUp(self):
        super().setUp()
        # Create sale order
        self.sale_order = self._create_so(self.partner_a)

    def test_01_create_project(self):
        # no project should be linked to this newly created SO
        self.assertFalse(self.sale_order.project_id)
        # store global proejct count for future compare
        project_count = self.project_model.search_count([])
        self.sale_order.action_create_project()
        # a newly created project should be linked to this SO
        self.assertTrue(self.sale_order.project_id)
        # project should be visible in sale form view
        self.assertTrue(self.sale_order.visible_project)
        # a new project should have been created
        self.assertEqual(self.project_model.search_count([]), project_count + 1)
        # only one contract should be linked to this project
        self.assertEqual(self.sale_order.project_id.contract_count, 1)
        # this SO shoud be the contract of this project
        self.assertEqual(self.sale_order.project_id.contract_ids, self.sale_order)
        # dates should be the same
        self.assertEqual(
            self.sale_order.project_id.contract_date_order, self.sale_order.date_order
        )
        project_count += 1
        project_id = self.sale_order.project_id
        self.sale_order.action_create_project()
        # the linked project should stay the same
        self.assertEqual(project_id, self.sale_order.project_id)
        # no new project should have been created
        self.assertEqual(self.project_model.search_count([]), project_count)
        # retry with override context key
        self.sale_order.with_context(override_project_id=True).action_create_project()
        # no new project should have been created
        self.assertEqual(self.project_model.search_count([]), project_count)
        # rename existing project name to "breaks" domain match
        project_id.name = project_id.name + "#1"
        # retry again with override context key
        self.sale_order.with_context(override_project_id=True).action_create_project()
        # a new project should have been created
        self.assertEqual(self.project_model.search_count([]), project_count + 1)
        project_count += 1
        # the newly created project should have replaced the old one
        self.assertNotEqual(project_id, self.sale_order.project_id)
        # old project should not be linked SO anymore
        self.assertFalse(project_id.contract_ids)
        # projects created when sale is in quotation should not be linked to each other
        self.assertFalse(self.sale_order.project_id.sale_order_id)
        # sale confirmation
        self.sale_order.action_confirm()
        # after quotation validation, project should be linked to its sale order
        self.assertEqual(self.sale_order, self.sale_order.project_id.sale_order_id)

    def test_02_task_from_so_line(self):
        # project should not be visible in sale form view
        self.assertFalse(self.sale_order.visible_project)
        # add a new service line
        sale_order_line = self._create_so_line(self.sale_order)
        # no project should be linked to this newly created SO
        self.assertFalse(self.sale_order.project_id)
        # but project could be visible now in sale form view (built-in logic)
        self.assertTrue(self.sale_order.visible_project)
        # sale confirmation
        self.sale_order.action_confirm()
        self.assertContract(self.sale_order, self.sale_order.project_id)
        # project should be visible in sale form view
        self.assertTrue(self.sale_order.visible_project)
        # a newly created project should be linked to this SO
        self.assertTrue(self.sale_order.project_id)
        task_id = self.sale_order.project_id.task_ids
        self.assertEqual(len(task_id), 1, "Only one task should exists")
        # customer should be the same on task and on SO
        self.assertEqual(task_id.partner_id, self.sale_order.partner_id)
        # task should not be excluded from sale order
        self.assertFalse(task_id.exclude_from_sale_order)
        # check everything is billable
        self.assertTrue(self.sale_order.project_id.allow_billable)
        self.assertTrue(task_id.allow_billable)
        # but it can be enforced
        self.assertEqual(task_id.sale_order_id, self.sale_order)
        self.assertEqual(task_id.sale_line_id, sale_order_line)
        task_id.exclude_from_sale_order = True
        task_id.invalidate_recordset()
        self.assertFalse(task_id.sale_order_id)
        self.assertFalse(task_id.sale_line_id)
        # task should not be billable anymore
        self.assertFalse(task_id.allow_billable)

    def test_03_task_from_so_line_existing_project(self):
        # project should not be visible in sale form view
        self.assertFalse(self.sale_order.visible_project)
        # add a new service line
        _so_line = self._create_so_line(self.sale_order)
        # no project should be linked to this newly created SO
        self.assertFalse(self.sale_order.project_id)
        # but project could be visible now in sale form view (built-in logic)
        self.assertTrue(self.sale_order.visible_project)
        # create project manually
        self.sale_order.action_create_project()
        # a newly created project should be linked to this SO
        self.assertTrue(self.sale_order.project_id)
        self.assertEqual(self.sale_order.project_id.contract_ids, self.sale_order)
        self.assertContract(self.sale_order, self.sale_order.project_id)
        # sale confirmation
        self.sale_order.action_confirm()
        # project should be visible in sale form view
        self.assertTrue(self.sale_order.visible_project)
        task_id = self.sale_order.project_id.task_ids
        self.assertEqual(task_id.sale_order_id, self.sale_order)
        task_id.invalidate_recordset()
        self.assertEqual(task_id.sale_order_id, self.sale_order)
        # create a new sale order
        new_sale_order = self._create_so(self.partner_a)
        new_sale_order.project_id = self.sale_order.project_id
        self.assertEqual(
            self.sale_order.project_id.contract_ids, self.sale_order + new_sale_order
        )
        # ensure task is always linked to its own sale order
        self.assertEqual(task_id.sale_order_id, self.sale_order)
        # add a new service line
        _new_so_line = self._create_so_line(new_sale_order)
        # sale confirmation
        new_sale_order.action_confirm()
        # get newly created task
        new_task_id = new_sale_order.project_id.task_ids - task_id
        new_task_id.invalidate_recordset()

    def test_04_task_so_from_project_contract(self):
        """Purpose of this test is to check `_compute_sale_order_id` behaviour, because
        it cannot be completly tested in a normal workflow because the `sale_order_id`
        value is pre-filled when task is created, so no computation is done.
        TODO: Check in Odoo > 14.0 if `modified` is called on non readonly computed
        fields in the create method"""
        _so_line = self._create_so_line(self.sale_order)
        # create project manually
        self.sale_order.action_create_project()
        # create a first task manually
        mt1_id = self.env["project.task"].create(
            {
                "name": "T1",
                "project_id": self.sale_order.project_id.id,
                "exclude_from_sale_order": False,
            }
        )
        self.assertEqual(mt1_id.sale_order_id, self.sale_order)
        # create a second task manually
        mt2_id = self.env["project.task"].create(
            {
                "name": "T2",
                "project_id": self.sale_order.project_id.id,
                "exclude_from_sale_order": False,
            }
        )
        self.assertEqual(mt2_id.sale_order_id, self.sale_order)
        # create a new sale order and assign it the same project
        new_sale_order = self._create_so(self.partner_a)
        new_sale_order.project_id = self.sale_order.project_id
        # project should now have two contracts
        self.assertEqual(
            self.sale_order.project_id.contract_ids, self.sale_order + new_sale_order
        )
        # create a third task manually
        mt3_id = self.env["project.task"].create(
            {
                "name": "T2",
                "project_id": self.sale_order.project_id.id,
                "exclude_from_sale_order": False,
            }
        )
        # no sale order should be automatically attached
        self.assertFalse(mt3_id.sale_order_id)
