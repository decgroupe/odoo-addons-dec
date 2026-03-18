# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from unittest.mock import patch

from odoo import Command, fields
from odoo.tests.common import TransactionCase

# pylint: disable=protected-access


class TestPurchaseStockTraceability(TransactionCase):
    def setUp(self):
        """create shared records for origin and action tests."""
        super().setUp()
        self.vendor = self.env["res.partner"].create({"name": "Traceability Vendor"})
        self.customer = self.env["res.partner"].create(
            {"name": "Traceability Customer"}
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Traceability Product",
                "type": "consu",
                "is_storable": True,
                "purchase_ok": True,
                "sale_ok": True,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.procurement_group_1 = self.env["procurement.group"].create(
            {"name": "PST/001", "move_type": "direct"}
        )
        self.procurement_group_2 = self.env["procurement.group"].create(
            {"name": "PST/002", "move_type": "direct"}
        )

    def _create_purchase_order(self):
        """create a draft purchase order with two lines."""
        return self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.display_name,
                            "product_id": self.product.id,
                            "product_qty": 1.0,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": 10.0,
                            "date_planned": fields.Datetime.now(),
                        }
                    ),
                    Command.create(
                        {
                            "name": self.product.display_name,
                            "product_id": self.product.id,
                            "product_qty": 2.0,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": 20.0,
                            "date_planned": fields.Datetime.now(),
                        }
                    ),
                ],
            }
        )

    def _create_purchase_line(self):
        """create a purchase line used by all origin tests."""
        purchase = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.display_name,
                            "product_id": self.product.id,
                            "product_qty": 1.0,
                            "product_uom": self.product.uom_po_id.id,
                            "price_unit": 10.0,
                            "date_planned": fields.Datetime.now(),
                        }
                    )
                ],
            }
        )
        return purchase.order_line

    def _create_sale_line(self):
        """create a sale line to use as move origin."""
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.display_name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        return sale.order_line

    def _create_move(self, sale_line=False, production=False, picking=False):
        """create a destination move with optional origin links."""
        return self.env["stock.move"].create(
            {
                "name": "Traceability Move",
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 1.0,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "sale_line_id": sale_line.id if sale_line else False,
                "raw_material_production_id": production.id if production else False,
                "picking_id": picking.id if picking else False,
            }
        )

    def test_01_purchase_line_requires_procurement_group_compat_field(self):
        """purchase line should expose the compatibility field used by this module."""
        self.assertIn("group_id", self.env["purchase.order"]._fields)
        # note: the `procurement_group_id` is added by `purchase_line_procurement_group`
        # module but there is also a built-in `group_id` now on this model recently
        # added by Odoo ... just ignore it !
        self.assertIn("procurement_group_id", self.env["purchase.order.line"]._fields)

    def test_02_write_group_updates_only_lines_without_procurement_group(self):
        """writing a group on the order should only backfill missing line groups."""
        order = self._create_purchase_order()
        line_1, line_2 = order.order_line
        line_2.write({"procurement_group_id": self.procurement_group_1.id})
        order.write({"group_id": self.procurement_group_2.id})
        self.assertEqual(line_1.procurement_group_id, self.procurement_group_2)
        self.assertEqual(line_2.procurement_group_id, self.procurement_group_1)

    def test_03_write_without_group_keeps_line_procurement_group_unchanged(self):
        """writing unrelated values should not change line procurement groups."""
        order = self._create_purchase_order()
        order.order_line.write({"procurement_group_id": self.procurement_group_1.id})
        order.write({"origin": "Updated origin"})
        self.assertEqual(
            order.order_line.mapped("procurement_group_id"), self.procurement_group_1
        )

    def test_10_get_origins_dict_with_all_supported_origins(self):
        """collect every supported origin from line fields and destination moves."""
        line = self._create_purchase_line()
        sale_line = self._create_sale_line()
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": 1.0,
            }
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "note": "delivery note",
            }
        )
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "name": "OP/PST",
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "product_min_qty": 1.0,
                "product_max_qty": 2.0,
                "qty_multiple": 1.0,
            }
        )
        move = self._create_move(
            sale_line=sale_line,
            production=production,
            picking=picking,
        )
        line.write(
            {
                "procurement_group_id": self.procurement_group_1.id,
                "orderpoint_ids": [Command.set([orderpoint.id])],
                "move_dest_ids": [Command.set([move.id])],
            }
        )
        origins = getattr(line, "_get_origins_dict")()  # noqa: B009
        self.assertEqual(origins["orderpoint_ids"], orderpoint)
        self.assertEqual(origins["production_ids"], production)
        self.assertEqual(origins["sale_line_ids"], sale_line)
        self.assertEqual(origins["sale_order_ids"], sale_line.order_id)
        self.assertEqual(origins["picking_ids"], picking)
        self.assertEqual(origins["procurement_group_id"], self.procurement_group_1)

    def test_11_get_origins_dict_uses_procurement_group_production_fallback(self):
        """fallback to procurement group production when moves have none."""
        line = self._create_purchase_line()
        line.procurement_group_id = self.procurement_group_1
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": 1.0,
                "procurement_group_id": self.procurement_group_1.id,
            }
        )
        origins = getattr(line, "_get_origins_dict")()  # noqa: B009
        self.assertEqual(origins["production_ids"], production)

    def test_12_format_origins_dict_includes_picking_note(self):
        """rendered origin html should include note block when picking has a note."""
        line = self._create_purchase_line()
        sale_line = self._create_sale_line()
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "note": "internal note",
            }
        )
        move = self._create_move(sale_line=sale_line, picking=picking)
        line.move_dest_ids = [Command.set([move.id])]
        origins = getattr(line, "_get_origins_dict")()  # noqa: B009
        html = line.format_origins_dict(origins, html=True)
        self.assertIn("🗳️", html)
        self.assertIn("📝", html)
        self.assertIn("internal note", html)

    def test_13_format_status_header_plaintext_and_html(self):
        """format status helper should support plain text and html rendering."""
        line = self._create_purchase_line()
        format_header = getattr(line, "_format_status_header")  # noqa: B009
        plain = format_header(["A", "B"], "draft", html=False)
        html = format_header(["A", "B"], "draft", html=True)
        self.assertEqual(plain, "A\nB")
        self.assertEqual(
            html,
            '<div class="d_move d_move_draft"><ul><li>A</li><li>B</li></ul></div>',
        )

    def test_14_action_view_origin_item_prefers_orderpoint(self):
        """action resolver should pick orderpoint first when multiple origins exist."""
        line = self._create_purchase_line()
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "name": "OP/PST/PRIO",
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "product_min_qty": 1.0,
                "product_max_qty": 2.0,
                "qty_multiple": 1.0,
            }
        )
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": 1.0,
            }
        )
        sale_line = self._create_sale_line()
        with patch.object(
            type(line),
            "_get_origins_dict",
            return_value={
                "orderpoint_ids": orderpoint,
                "production_ids": production,
                "sale_order_ids": sale_line.order_id,
                "procurement_group_id": self.procurement_group_1,
            },
        ):
            action = line.action_view_origin_item()
        self.assertEqual(action["res_model"], "stock.warehouse.orderpoint")

    def test_15_action_view_origin_item_fallbacks(self):
        """action resolver should fallback in expected priority order."""
        line = self._create_purchase_line()
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_qty": 1.0,
            }
        )
        sale_line = self._create_sale_line()
        with patch.object(
            type(line),
            "_get_origins_dict",
            return_value={"production_ids": production},
        ):
            action_production = line.action_view_origin_item()
        with patch.object(
            type(line),
            "_get_origins_dict",
            return_value={"sale_order_ids": sale_line.order_id},
        ):
            action_sale = line.action_view_origin_item()
        with patch.object(
            type(line),
            "_get_origins_dict",
            return_value={"procurement_group_id": self.procurement_group_1},
        ):
            action_group = line.action_view_origin_item()
        with patch.object(type(line), "_get_origins_dict", return_value={}):
            action_none = line.action_view_origin_item()
        self.assertEqual(action_production["res_model"], "mrp.production")
        self.assertEqual(action_sale["res_model"], "sale.order")
        self.assertEqual(action_group["res_model"], "procurement.group")
        self.assertFalse(action_none)

    def test_16_compute_origin_visibility_is_false_for_picking_only(self):
        """picking-only origin should not enable the action button visibility."""
        line = self._create_purchase_line()
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "note": "only picking",
            }
        )
        with patch.object(
            type(line),
            "_get_origins_dict",
            return_value={"picking_ids": picking},
        ):
            getattr(line, "_compute_origin")()  # noqa: B009
        self.assertFalse(line.action_view_origin_item_visible)
        self.assertIn("only picking", line.procurement_origin)

    def test_17_run_buy_context_postprocess_adds_message(self):
        """purchase create and search should execute run_buy postprocess."""
        purchase_model = self.env["purchase.order"].with_context(
            run_buy=True,
            message_post_to_po="postprocess message",
            buyer=self.env.user.id,
        )
        purchase = purchase_model.create({"partner_id": self.vendor.id})
        self.assertTrue(
            purchase.message_ids.filtered(
                lambda m: "postprocess message" in (m.body or "")
            )
        )
        purchase_model.search([("id", "=", purchase.id)])
        self.assertTrue(
            purchase.message_ids.filtered(
                lambda m: "postprocess message" in (m.body or "")
            )
        )
