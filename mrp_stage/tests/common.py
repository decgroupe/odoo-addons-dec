# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023


from odoo import Command
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestMrpStageBase(TransactionCase):
    """Base class for testing mrp_stage"""

    def _create_component_in_bom(self, name, bom):
        product = self.env["product.product"].create(
            {
                "name": f"Component {name}",
                "type": "consu",
                "is_storable": True,
            }
        )
        self.env["mrp.bom.line"].create(
            {"product_id": product.id, "product_qty": 1, "bom_id": bom.id}
        )
        return product

    @mute_logger("odoo.addons.stock.models.stock_rule")
    def _run_scheduler(self):
        self.env["procurement.group"].run_scheduler()

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.production_model = self.env["mrp.production"]
        self.stage_model = self.env["mrp.production.stage"]
        self.product_model = self.env["product.product"]
        self.bom_model = self.env["mrp.bom"]
        self.boml_model = self.env["mrp.bom.line"]

        self.warehouse1 = self.env.ref("stock.warehouse0")
        # self.route_buy = self.warehouse1.buy_pull_id.route_id
        self.route_mto = self.warehouse1.mto_pull_id.route_id
        self.route_mto.active = True
        self.route_manufacture = self.warehouse1.manufacture_pull_id.route_id

        # create a manufacturable product with a BoM to test the mrp status of moves
        self.manufacturable_product = self.product_model.create(
            {
                "name": "Manufacturable Product",
                "type": "consu",
                "is_storable": True,
                "route_ids": [
                    Command.set([self.route_mto.id, self.route_manufacture.id])
                ],
            }
        )
        # create a BoM for the manufacturable product
        self.bom = self.bom_model.create(
            {
                "product_tmpl_id": self.manufacturable_product.product_tmpl_id.id,
                "product_id": self.manufacturable_product.id,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "bom_line_ids": [],
            }
        )
        # create a component
        self.product1 = self._create_component_in_bom("#1", self.bom)
