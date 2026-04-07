# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from .common import TestMrpProductionRequestProcurementCommon


class TestMrpProductionRequestProcurement(TestMrpProductionRequestProcurementCommon):
    """Tests for mrp_production_request_procurement module."""

    def test_01_production_name_set_on_create(self):
        """Creating a request with picking_type_id generates production_name
        and derives the request name from it."""
        request = self._create_production_request(qty=1.0)
        self.assertTrue(request.production_name)
        # name should be production_name with "MO" replaced by "MR"
        expected_name = request.production_name.replace("MO", "MR")
        self.assertEqual(request.name, expected_name)

    def test_02_approval_creates_common_procurement_group(self):
        """Approving a request with use_common_procurement_group=True creates
        a procurement group named after the production prefix."""
        request = self._create_production_request(qty=1.0)
        request.write({"use_common_procurement_group": True})
        request.button_to_approve()
        request.button_approved()
        self.assertTrue(request.common_procurement_group_id)
        self.assertEqual(
            request.common_procurement_group_id.name,
            request.production_name,
        )

    def test_03_approval_skips_group_when_flag_not_set(self):
        """Approving a request without use_common_procurement_group does not
        create a common procurement group."""
        request = self._create_production_request(qty=1.0)
        request.button_to_approve()
        request.button_approved()
        self.assertFalse(request.common_procurement_group_id)

    def test_04_approval_skips_group_when_already_set(self):
        """Approving a request that already has a common_procurement_group_id
        does not replace the existing group."""
        request = self._create_production_request(qty=1.0)
        existing_group = self.env["procurement.group"].create(
            {"name": "Existing Group"}
        )
        request.write(
            {
                "use_common_procurement_group": True,
                "common_procurement_group_id": existing_group.id,
            }
        )
        request.button_to_approve()
        request.button_approved()
        self.assertEqual(request.common_procurement_group_id, existing_group)

    def test_05_wizard_uses_common_procurement_group(self):
        """The wizard assigns common_procurement_group_id to the MO when the
        flag is set on the request."""
        request = self._create_production_request(qty=1.0)
        request.write({"use_common_procurement_group": True})
        request.button_to_approve()
        request.button_approved()
        self.assertTrue(request.common_procurement_group_id)
        wizard = self._create_wizard(request)
        vals = wizard._prepare_manufacturing_order()
        self.assertEqual(
            vals["procurement_group_id"],
            request.common_procurement_group_id.id,
        )

    def test_06_wizard_clears_procurement_group_when_flag_not_set(self):
        """The wizard sets procurement_group_id to False when
        use_common_procurement_group is disabled."""
        request = self._create_production_request(qty=1.0)
        request.button_to_approve()
        request.button_approved()
        wizard = self._create_wizard(request)
        vals = wizard._prepare_manufacturing_order()
        self.assertFalse(vals["procurement_group_id"])

    def test_07_mo_name_equals_production_name_for_single_qty(self):
        """MO name is the bare production_name when product_qty=1 and no
        previous MOs have been created."""
        request = self._create_production_request(qty=1.0)
        request.button_to_approve()
        request.button_approved()
        wizard = self._create_wizard(request)
        vals = wizard._prepare_manufacturing_order()
        self.assertEqual(vals["name"], request.production_name)

    def test_08_mo_name_uses_index_for_multiple_qty(self):
        """MO name uses an indexed suffix when product_qty > 1."""
        request = self._create_production_request(qty=2.0)
        request.button_to_approve()
        request.button_approved()
        wizard = self._create_wizard(request)
        vals = wizard._prepare_manufacturing_order()
        expected_name = f"{request.production_name}/01"
        self.assertEqual(vals["name"], expected_name)

    # def test_09_production_name_set_without_picking_type(self):
    #     """Creating a request without a picking_type_id still generates a
    #     production_name using the mrp.production sequence as fallback."""
    #     request = self.request_model.create(
    #         {
    #             "product_id": self.product.id,
    #             "bom_id": self.bom.id,
    #             "product_qty": 1.0,
    #         }
    #     )
    #     self.assertTrue(request.production_name)
