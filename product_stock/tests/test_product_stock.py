# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

import datetime
import random

from freezegun import freeze_time

from . import common


class TestProductStock(common.TestProductStockCommon):
    """Tests for the product_stock module."""

    def setUp(self):
        """Prepare a stable reference timestamp for each test."""
        super().setUp()
        self.now = self._now() + datetime.timedelta(days=10)

    def test_01_no_product_last_move(self):
        """Verify empty recordsets do not compute stock move values."""
        empty_products = self.Product.browse()
        self.assertFalse(empty_products.last_move_id)
        self.assertFalse(empty_products.last_move_date)

    def test_02_product_last_move(self):
        """Verify the latest non-draft move is selected per product."""
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
        with freeze_time(self.now + datetime.timedelta(days=100)):
            self._adjust_inventory(
                self.location_stock,
                [self.product_drawer, self.product_flipover, self.product_storagebox],
                [10, 20, 30],
            )
        with freeze_time(self.now + datetime.timedelta(days=150)):
            self._adjust_inventory(
                self.location_stock,
                [self.product_drawer],
                [5],
            )
        with freeze_time(self.now + datetime.timedelta(days=151)):
            self._adjust_inventory(
                self.location_stock,
                [self.product_flipover],
                [10],
            )

    def test_03_search_need_inventory_update(self):
        """Verify products without recent inventories are returned."""
        self._create_fake_inventories()
        inventory_start_date = self.now + datetime.timedelta(days=150)
        res = self.Product.search_need_inventory_update(inventory_start_date)
        self.assertNotIn(self.product_drawer.id, res)
        self.assertNotIn(self.product_flipover.id, res)
        self.assertIn(self.product_storagebox.id, res)

    def test_04_search_inventory_done_at_location(self):
        """Verify products inventoried at a location are returned."""
        self._create_fake_inventories()
        inventory_start_date = self.now + datetime.timedelta(days=150)
        res = self.Product.search_inventory_done_at_location(
            inventory_start_date, self.location_stock.id
        )
        self.assertIn(self.product_drawer.id, res)
        self.assertIn(self.product_flipover.id, res)
        self.assertNotIn(self.product_storagebox.id, res)

    def test_05_no_product_last_inventory(self):
        """Verify empty recordsets do not compute inventory values."""
        empty_products = self.Product.browse()
        self.assertFalse(empty_products.last_inventory_line_id)
        self.assertFalse(empty_products.last_inventory_quantity)
        self.assertFalse(empty_products.last_inventory_date)

    def test_06_last_inventory(self):
        """Verify the latest inventory move line is selected per product."""
        # create fake inventory adjustments
        for days in [2, 5, 8]:
            with freeze_time(self.now + datetime.timedelta(days=days)):
                self._adjust_inventory(
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
        with freeze_time(self.now + datetime.timedelta(days=10)):
            self._adjust_inventory(
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
        (self.product_drawer + self.product_flipover + self.product_storagebox).mapped(
            "last_inventory_line_id"
        )
        self.assertEqual(self.product_drawer.last_inventory_line_id.quantity, 45)
        self.assertEqual(self.product_flipover.last_inventory_line_id.quantity, 90)
        self.assertEqual(self.product_storagebox.last_inventory_line_id.quantity, 120)
