# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo import Command
from odoo.fields import UserError
from odoo.tests.common import TransactionCase


class TestMrpWarnings(TransactionCase):
    def setUp(self):
        super().setUp()
        self.production_model = self.env["mrp.production"]
        self.bom_model = self.env["mrp.bom"]
        self.bom_line_model = self.env["mrp.bom.line"]
        self.product_model = self.env["product.product"]

        route_manuf = self.env.ref("mrp.route_warehouse0_manufacture")
        self.product = self.env.ref("product.product_product_3")
        self.product.route_ids = [Command.link(route_manuf.id)]

        self.product_component = self.product_model.create(
            {
                "name": "Test component",
                "route_ids": [Command.set([route_manuf.id])],
            }
        )

        # Create Bill of Materials:
        self.bom = self.bom_model.create(
            {
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        self.bom_line_model.create(
            {
                "bom_id": self.bom.id,
                "product_id": self.product_component.id,
                "product_qty": 1.0,
            }
        )

    def _create_production(self):
        return self.production_model.create(
            {
                "product_id": self.product.id,
                "product_qty": 1,
                "product_uom_id": self.product.uom_id.id,
                "bom_id": self.bom.id,
            }
        )

    def test_01_create_production(self):
        production1 = self._create_production()
        self.assertEqual(production1.state, "draft")
        self.assertEqual(production1.bom_id, self.bom)
        production1.action_confirm()
        self.assertEqual(production1.state, "confirmed")

    def test_02_update_existing_production(self):
        production1 = self._create_production()
        # set component product to inactive
        self.product_component.action_archive()
        # try to confirm existing production
        ERROR_MSG = f"{self.product_component.display_name} is obsolete"
        with self.assertRaisesRegex(UserError, ERROR_MSG), self.cr.savepoint():
            production1.action_confirm()

    def test_03_create_production_with_obsolete_component(self):
        # set component product to obsolete
        self.product_component.state = "obsolete"
        # try to create a new production
        ERROR_MSG = f"{self.product_component.display_name} is obsolete"
        with self.assertRaisesRegex(UserError, ERROR_MSG), self.cr.savepoint():
            self._create_production()

    def test_04_create_production_bom_with_inactive_component(self):
        # set component product to inactive
        self.product_component.action_archive()
        # try to create a new production
        ERROR_MSG = f"{self.product_component.display_name} is archived"
        with self.assertRaisesRegex(UserError, ERROR_MSG), self.cr.savepoint():
            self._create_production()
