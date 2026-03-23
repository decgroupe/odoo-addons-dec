# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestMrpProductionRequestAutoConfirm(TransactionCase):
    """Test case for the mrp_production_request_auto_confirm module."""

    def setUp(self, *args, **kwargs):
        """Set up test fixtures: product, BoM, and production request."""
        super().setUp(*args, **kwargs)
        self.request_model = self.env["mrp.production.request"]
        self.production_model = self.env["mrp.production"]
        self.wiz_model = self.env["mrp.production.request.create.mo"]
        route_manufacture = self.env.ref("mrp.route_warehouse0_manufacture")
        product_component = self.env["product.product"].create(
            {
                "name": "Auto Confirm Test Component",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Auto Confirm Test Product",
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

    def _create_approved_request(self, qty=2.0):
        """Create and approve a manufacturing request for self.product."""
        request = self.request_model.create(
            {
                "product_id": self.product.id,
                "bom_id": self.bom.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": qty,
                "date_start": fields.Datetime.now(),
                "date_finished": fields.Datetime.now(),
            }
        )
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

    def test_01_mo_auto_confirmed(self):
        """Test that MO created from production request is automatically confirmed."""
        request = self._create_approved_request(qty=2.0)
        action = self._create_mo_using_wizard(request, 2.0)
        mo = self.production_model.browse(action["res_id"])
        self.assertTrue(mo)
        self.assertEqual(mo.state, "confirmed")
