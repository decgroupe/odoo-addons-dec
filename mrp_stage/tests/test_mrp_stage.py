from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests.common import Form, TransactionCase, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestMrpStage(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.production_model = self.env["mrp.production"]
        self.stage_model = self.env["mrp.production.stage"]
        self.product_model = self.env["product.product"]
        self.bom_model = self.env["mrp.bom"]
        self.boml_model = self.env["mrp.bom.line"]

        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_loc = self.env.ref("stock.stock_location_stock")
        route_manuf = self.env.ref("mrp.route_warehouse0_manufacture")

        # Prepare Products:
        self.product = self.env.ref("product.product_product_3")
        self.product.route_ids = [(4, route_manuf.id, 0)]

        product_component = self.product_model.create(
            {
                "name": "Test component",
                "route_ids": [(6, 0, route_manuf.ids)],
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
        self.boml_model.create(
            {
                "bom_id": self.bom.id,
                "product_id": product_component.id,
                "product_qty": 1.0,
            }
        )

        # Create User:
        self.test_user = self.env["res.users"].create({"name": "John", "login": "test"})

    @mute_logger("odoo.addons.stock.models.stock_rule")
    def _run_scheduler(self):
        self.env["procurement.group"].run_scheduler()

    def test_01_validate_mo_states(self):
        """Tests that all hard-coded manufacturing order states have a stage match"""
        state_field = self.production_model._fields["state"]
        mo_states = [s[0] for s in state_field.selection]
        stages = self.production_model._get_stages_ref()
        for state in mo_states:
            self.assertIn(state, stages)
