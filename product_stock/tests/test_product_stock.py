# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

import datetime
import random

from freezegun import freeze_time

from odoo.tests.common import SavepointCase


class TestProductStock(SavepointCase):

    def _now(self):
        now = datetime.datetime.now().replace(microsecond=0)
        return now

    def _create_stock_move(
        self, product_id, qty=10, location_id=None, location_dest_id=None
    ):
        if location_id is None:
            location_id = self.location_stock
        if location_dest_id is None:
            location_dest_id = self.location_customers
        move_id = self.StockMove.create(
            {
                "name": "Test Move",
                "product_id": product_id.id,
                "product_uom": product_id.uom_id.id,
                "product_uom_qty": qty,
                "location_id": location_id.id,
                "location_dest_id": location_dest_id.id,
            }
        )
        return move_id

    # copy/paste from "point_of_sale/tests/common.py"
    @classmethod
    def adjust_inventory(cls, location_id, products, quantities):
        """Adjust inventory of the given products"""
        stock_inventory = cls.env["stock.inventory"].create(
            {"name": "Inventory adjustment"}
        )
        for product, qty in zip(products, quantities):
            cls.env["stock.inventory.line"].create(
                {
                    "product_id": product.id,
                    "product_uom_id": product.uom_id.id,
                    "inventory_id": stock_inventory.id,
                    "product_qty": qty,
                    "location_id": location_id.id,
                }
            )
        stock_inventory._action_start()
        stock_inventory.action_validate()

    # class setup
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # models
        cls.Product = cls.env["product.product"]
        cls.StockMoveLine = cls.env["stock.move.line"]
        cls.StockMove = cls.env["stock.move"]
        # stock locations
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_customers = cls.env.ref("stock.stock_location_customers")
        # ref to [E-COM08] Storage Box
        cls.product_storagebox = cls.env.ref("product.product_product_7")
        # ref to [FURN_8855] Drawer
        cls.product_drawer = cls.env.ref("product.product_product_27")
        # ref to [FURN_9001] Flipover
        cls.product_flipover = cls.env.ref("product.product_product_20")

    def setUp(self):
        super().setUp()
        self.now = self._now() + datetime.timedelta(days=10)

    def test_01_no_product_last_move(self):
        self.Product._compute_last_stock_move()
        self.assertFalse(self.Product.last_move_id)
        self.assertFalse(self.Product.last_move_date)

    def test_02_product_last_move(self):
        # create multiple stock moves at different dates
        product_drawer_move_ids = self.StockMove
        product_flipover_move_ids = self.StockMove
        for days in [0, 5, 2, 3, 4, 10, 20]:
            with freeze_time(self.now + datetime.timedelta(days=days)):
                product_drawer_move_ids |= self._create_stock_move(
                    self.product_drawer,
                )
                # only confirm the move if the date is less than 10 days in the future
                if days < 10:
                    product_drawer_move_ids._action_confirm()
        for days in [2, 3, 4, 1, 15, 25]:
            with freeze_time(self.now + datetime.timedelta(days=days)):
                product_flipover_move_ids |= self._create_stock_move(
                    self.product_flipover,
                )
                # only confirm the move if the date is less than 10 days in the future
                if days < 10:
                    product_flipover_move_ids._action_confirm()
        # check that the last move id is the more recent one (ignore draft moves)
        self.assertEqual(
            self.product_drawer.last_move_id,
            product_drawer_move_ids[1],
        )
        self.assertEqual(
            self.product_flipover.last_move_id,
            product_flipover_move_ids[2],
        )
        # also check that the last move date match
        self.assertEqual(
            self.product_drawer.last_move_date, self.now + datetime.timedelta(days=5)
        )
        self.assertEqual(
            self.product_flipover.last_move_date, self.now + datetime.timedelta(days=4)
        )

    def _create_fake_inventories(self):
        # create fake inventory adjustments at NOW + 100days
        with freeze_time(self.now + datetime.timedelta(days=100)):
            self.adjust_inventory(
                self.location_stock,
                [self.product_drawer, self.product_flipover, self.product_storagebox],
                [10, 20, 30],
            )
        # create fake inventory adjustments at NOW + 150days
        with freeze_time(self.now + datetime.timedelta(days=150)):
            self.adjust_inventory(
                self.location_stock,
                [self.product_drawer],
                [5],
            )
        # create fake inventory adjustments at NOW + 151days
        with freeze_time(self.now + datetime.timedelta(days=151)):
            self.adjust_inventory(
                self.location_stock,
                [self.product_flipover],
                [10],
            )

    def test_03_search_need_inventory_update(self):
        self._create_fake_inventories()
        # check
        inventory_start_date = self.now + datetime.timedelta(days=150)
        res = self.Product.search_need_inventory_update(inventory_start_date)
        self.assertNotIn(self.product_drawer.id, res)
        self.assertNotIn(self.product_flipover.id, res)
        self.assertIn(self.product_storagebox.id, res)

    def test_04_search_inventory_done_at_location(self):
        self._create_fake_inventories()
        # check
        inventory_start_date = self.now + datetime.timedelta(days=150)
        res = self.Product.search_inventory_done_at_location(
            inventory_start_date, self.location_stock.id
        )
        self.assertIn(self.product_drawer.id, res)
        self.assertIn(self.product_flipover.id, res)
        self.assertNotIn(self.product_storagebox.id, res)

    def test_05_no_product_last_inventory(self):
        self.Product._compute_last_inventory()
        self.assertFalse(self.Product.last_inventory_line_id)
        self.assertFalse(self.Product.last_inventory_quantity)
        self.assertFalse(self.Product.last_inventory_date)

    def test_06_last_inventory(self):
        # create fake inventory adjustments
        for days in [2, 5, 8]:
            with freeze_time(self.now + datetime.timedelta(days=days)):
                self.adjust_inventory(
                    self.location_stock,
                    [
                        self.product_drawer,
                        self.product_flipover,
                        self.product_storagebox,
                    ],
                    [
                        10 + random.randint(0, 50),
                        20 + random.randint(0, 50),
                        30 + random.randint(0, 50),
                    ],
                )
        # for quantities for the last inventory
        with freeze_time(self.now + datetime.timedelta(days=10)):
            self.adjust_inventory(
                self.location_stock,
                [
                    self.product_drawer,
                    self.product_flipover,
                    self.product_storagebox,
                ],
                [
                    45,
                    90,
                    120,
                ],
            )
        # prefetch
        (self.product_drawer + self.product_flipover + self.product_storagebox).mapped(
            "last_inventory_line_id"
        )
        # check that the last inventory line is the more recent one
        self.assertEqual(self.product_drawer.last_inventory_line_id.product_qty, 45)
        self.assertEqual(self.product_flipover.last_inventory_line_id.product_qty, 90)
        self.assertEqual(
            self.product_storagebox.last_inventory_line_id.product_qty, 120
        )
