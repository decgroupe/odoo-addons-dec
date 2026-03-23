# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestMrpProductionRequestProject(TransactionCase):
    """Test that the project is propagated from sale order to MO via the wizard."""

    def setUp(self, *args, **kwargs):
        """Set up product, BoM, sale order and project fixtures."""
        super().setUp(*args, **kwargs)
        self.request_model = self.env["mrp.production.request"]
        self.production_model = self.env["mrp.production"]
        self.wiz_model = self.env["mrp.production.request.create.mo"]
        route_manufacture = self.env.ref("mrp.route_warehouse0_manufacture")
        product_component = self.env["product.product"].create(
            {
                "name": "Project Test Component",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Project Test Product",
                "mrp_production_request": True,
                "route_ids": [Command.set(route_manufacture.ids)],
            }
        )
        self.bom = self.env["mrp.bom"].create(
            {
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {"product_id": product_component.id, "product_qty": 1.0}
                    ),
                ],
            }
        )
        self.project = self.env["project.project"].create(
            {
                "name": "Project Test",
            }
        )
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "project_id": self.project.id,
            }
        )

    def _create_approved_request(self, qty=1.0, sale_order=None):
        """Create and approve a manufacturing request optionally linked to a SO."""
        vals = {
            "product_id": self.product.id,
            "bom_id": self.bom.id,
            "product_uom_id": self.product.uom_id.id,
            "product_qty": qty,
            "date_start": fields.Datetime.now(),
            "date_finished": fields.Datetime.now(),
        }
        if sale_order:
            vals["sale_order_id"] = sale_order.id
        request = self.request_model.create(vals)
        request.button_to_approve()
        request.button_approved()
        return request

    def _create_mo_using_wizard(self, request, qty):
        """Use the wizard to create the manufacturing order."""
        ctx = {
            "active_ids": request.ids,
            "active_model": "mrp.production.request",
        }
        wizard = self.wiz_model.with_context(**ctx).create({})
        wizard.mo_qty = qty
        action = wizard.create_mo()
        return action

    def test_01_project_propagated_from_sale_order(self):
        """Test that project_id is copied from sale order to MO."""
        request = self._create_approved_request(qty=1.0, sale_order=self.sale_order)
        self.assertEqual(request.sale_order_id, self.sale_order)
        action = self._create_mo_using_wizard(request, 1.0)
        mo = self.production_model.browse(action["res_id"])
        self.assertTrue(mo)
        self.assertEqual(
            mo.project_id,
            self.project,
            "MO project_id should match the sale order's project_id.",
        )

    def test_02_no_project_without_sale_order(self):
        """Test that project_id is not set on MO when no sale order is linked."""
        request = self._create_approved_request(qty=1.0, sale_order=None)
        self.assertFalse(request.sale_order_id)
        action = self._create_mo_using_wizard(request, 1.0)
        mo = self.production_model.browse(action["res_id"])
        self.assertTrue(mo)
        self.assertFalse(
            mo.project_id,
            "MO project_id should not be set when no sale order is linked.",
        )

    def test_03_no_project_when_sale_order_has_no_project(self):
        """Test MO has no project when the sale order has no project."""
        sale_order_no_project = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
            }
        )
        request = self._create_approved_request(
            qty=1.0, sale_order=sale_order_no_project
        )
        action = self._create_mo_using_wizard(request, 1.0)
        mo = self.production_model.browse(action["res_id"])
        self.assertTrue(mo)
        self.assertFalse(
            mo.project_id,
            "MO project_id should not be set when sale order has no project.",
        )
