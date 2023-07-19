# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common


class TestProcurementRunManufactureWarnings(common.TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.warehouse1 = self.env.ref("stock.warehouse0")

        self.route_mto = self.warehouse1.mto_pull_id.route_id
        self.route_manufacture = self.warehouse1.manufacture_pull_id.route_id
        self.unit_uom_id = self.env.ref("uom.product_uom_unit")

    def _create_make_procurement(
        self, product, product_qty, uom_id, warehouse_id, date_planned=False
    ):
        ProcurementGroup = self.env["procurement.group"]
        order_values = {
            "warehouse_id": warehouse_id,
            "action": "pull_push",
            "date_planned": date_planned
            or fields.Datetime.to_string(fields.datetime.now() + timedelta(days=10)),
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

    def test_manufacture_inactive_product(self):
        """ """
        product_inactive_id = self.env["product.product"].create(
            {
                "active": False,
                "name": "Product",
                "type": "product",
                "uom_id": self.unit_uom_id.id,
                "route_ids": [(6, 0, [self.route_manufacture.id, self.route_mto.id])],
            }
        )
        bom_id = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": product_inactive_id.product_tmpl_id.id,
                "product_uom_id": self.unit_uom_id.id,
                "sequence": 1,
            }
        )
        try:
            self._create_make_procurement(
                product_inactive_id,
                15.00,
                product_inactive_id.uom_id,
                self.warehouse1,
            )
        except UserError as user_error:
            self.assertTrue(
                "Cannot manufacture product %s, because it is archived"
                % (product_inactive_id.name)
                in user_error.name
            )
            self.assertTrue(
                "Please add at least one component to this Bill of Material"
                in user_error.name
            )
            print(user_error)
