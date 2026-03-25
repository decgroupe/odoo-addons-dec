# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import fields
from odoo.fields import Command
from odoo.tests import TransactionCase


class TestPurchaseStockGroupEmpty(TransactionCase):
    """Test that procurements without group_id only use/create POs with
    group_id = False."""

    @classmethod
    def setUpClass(cls):
        """Set up shared fixtures: warehouse, company and buy rule."""
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.company = cls.env.company
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.mto_route.active = True
        cls.buy_route = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.buy_rule = cls.buy_route.rule_ids.filtered(
            lambda rule: rule.warehouse_id == cls.warehouse
        )
        cls.assertTrue(
            cls.buy_rule, "Expected a buy rule for the warehouse's buy route"
        )

    def setUp(self):
        """Set up per-test fixtures: supplier, product and supplierinfo."""
        super().setUp()
        self.supplier = self.env["res.partner"].create({"name": "Test Supplier PSGE"})
        self.product = self.env["product.product"].create(
            {
                "name": "Test Product PSGE",
                "type": "consu",
                "is_storable": True,
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": self.supplier.id,
                            "price": 10.0,
                        }
                    )
                ],
                "route_ids": [
                    Command.set(
                        [
                            self.buy_route.id,
                            self.mto_route.id,
                        ]
                    )
                ],
            }
        )
        self.supplierinfo = self.product.seller_ids[0]

    def _make_procurement(self):
        """Return a Procurement namedtuple for self.product without group_id."""
        return self.env["procurement.group"].Procurement(
            self.product,
            5.0,
            self.product.uom_id,
            self.warehouse.lot_stock_id,
            "Test PSGE",
            "Test PSGE Origin",
            self.company,
            {
                "warehouse_id": self.warehouse,
                "date_planned": fields.Datetime.now(),
            },
        )

    def test_01_domain_without_group_id_contains_false_constraint(self):
        """When values have no group_id, the domain must include
        ('group_id', '=', False)."""
        values = {
            "supplier": self.supplierinfo,
            "date_planned": fields.Datetime.now(),
            "warehouse_id": self.warehouse,
        }
        domain = self.buy_rule._make_po_get_domain(self.company, values, self.supplier)
        self.assertIn(
            ("group_id", "=", False),
            domain,
            "domain must contain ('group_id', '=', False) when no group_id is set",
        )

    def test_02_domain_with_group_id_no_false_constraint(self):
        """When values carry a group_id (propagated), the domain must NOT
        include ('group_id', '=', False) but must include the actual group."""
        group = self.env["procurement.group"].create({"name": "Test Group PSGE"})
        self.buy_rule.group_propagation_option = "propagate"
        values = {
            "supplier": self.supplierinfo,
            "date_planned": fields.Datetime.now(),
            "warehouse_id": self.warehouse,
            "group_id": group,
        }
        domain = self.buy_rule._make_po_get_domain(self.company, values, self.supplier)
        self.assertNotIn(
            ("group_id", "=", False),
            domain,
            "domain must NOT contain ('group_id', '=', False) when group_id is set",
        )
        self.assertIn(
            ("group_id", "=", group.id),
            domain,
            "domain must contain the procurement group constraint",
        )

    def test_03_procurement_without_group_creates_po_without_group(self):
        """Running a procurement without group_id must create a PO whose
        group_id is False."""
        self.env["procurement.group"].run([self._make_procurement()])
        po = self.env["purchase.order"].search([("partner_id", "=", self.supplier.id)])
        self.assertEqual(len(po), 1)
        self.assertFalse(po.group_id, "created PO must have group_id = False")

    def test_04_two_procurements_without_group_merged_into_same_po(self):
        """Two procurements without group_id must be merged into the same PO
        because both domains filter on group_id = False. Since the product is
        identical, Odoo merges them into a single line with the combined qty."""
        self.env["procurement.group"].run([self._make_procurement()])
        self.env["procurement.group"].run([self._make_procurement()])
        pos = self.env["purchase.order"].search([("partner_id", "=", self.supplier.id)])
        self.assertEqual(
            len(pos),
            1,
            "both procurements must be merged into a single PO",
        )
        self.assertEqual(
            len(pos.order_line),
            1,
            "same-product procurements on the same PO are merged into one line",
        )
        self.assertAlmostEqual(
            pos.order_line.product_qty,
            10.0,
            msg="the merged line must carry the combined quantity of both procurements",
        )

    def test_05_procurement_without_group_not_merged_into_grouped_po(self):
        """A procurement without group_id must NOT be merged into an existing
        PO that has a group_id set."""
        group = self.env["procurement.group"].create({"name": "Test Group PSGE"})
        # create an existing draft PO belonging to a procurement group
        existing_po = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
                "picking_type_id": self.warehouse.in_type_id.id,
                "company_id": self.company.id,
                "currency_id": self.company.currency_id.id,
                "group_id": group.id,
            }
        )
        # run a procurement without group_id, must NOT merge into existing_po
        self.env["procurement.group"].run([self._make_procurement()])
        pos = self.env["purchase.order"].search([("partner_id", "=", self.supplier.id)])
        self.assertEqual(
            len(pos),
            2,
            "a new PO must be created instead of merging into the grouped PO",
        )
        new_po = pos - existing_po
        self.assertFalse(
            new_po.group_id,
            "the newly created PO must have group_id = False",
        )
